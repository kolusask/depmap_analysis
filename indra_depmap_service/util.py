"""Utility functions for the INDRA Causal Network Search API in api.py"""
import re
import json
import logging
import argparse
import platform

from os import path, stat
from datetime import datetime

import networkx as nx
from fnvhash import fnv1a_32

from indra_db.client.readonly.query import FromMeshIds
from indra_db.util.dump_sif import load_db_content, make_dataframe, NS_LIST
from indra.statements import get_all_descendants, Activation, Inhibition, \
    IncreaseAmount, DecreaseAmount, AddModification, RemoveModification, \
    Complex
from depmap_analysis.network_functions import net_functions as nf
from depmap_analysis.util.io_functions import pickle_open, dump_it_to_pickle
from depmap_analysis.util.aws import get_latest_sif_s3, dump_json_to_s3, \
    dump_pickle_to_s3, NEW_NETS_PREFIX

logger = logging.getLogger('INDRA Network Search util')

API_PATH = path.dirname(path.abspath(__file__))
CACHE = path.join(API_PATH, '_cache')
STATIC = path.join(API_PATH, 'static')
JSON_CACHE = path.join(API_PATH, '_json_res')
DT_YmdHMS_ = '%Y-%m-%d-%H-%M-%S'
DT_YmdHMS = '%Y%m%d%H%M%S'
DT_Ymd = '%Y%m%d'
RE_YmdHMS_ = r'\d{4}\-\d{2}\-\d{2}\-\d{2}\-\d{2}\-\d{2}'
RE_YYYYMMDD = r'\d{8}'

INDRA_MDG = 'indranet_multi_digraph_latest.pkl'
INDRA_DG = 'indranet_dir_graph_latest.pkl'
INDRA_SNG = 'indranet_sign_node_graph_latest.pkl'
INDRA_SEG = 'indranet_sign_edge_graph_latest.pkl'
INDRA_PBSNG = 'indranet_sign_node_pybel_latest.pkl'
INDRA_PBSEG = 'indranet_sign_edge_pybel_latest.pkl'

TEST_MDG_CACHE = path.join(CACHE, 'test_mdg_network.pkl')
INDRA_MDG_CACHE = path.join(CACHE, INDRA_MDG)
TEST_DG_CACHE = path.join(CACHE, 'test_dir_network.pkl')
INDRA_DG_CACHE = path.join(CACHE, INDRA_DG)
INDRA_SNG_CACHE = path.join(CACHE, INDRA_SNG)
INDRA_SEG_CACHE = path.join(CACHE, INDRA_SEG)
INDRA_PBSNG_CACHE = path.join(CACHE, INDRA_PBSNG)
INDRA_PBSEG_CACHE = path.join(CACHE, INDRA_PBSEG)


def todays_date():
    return datetime.now().strftime(DT_Ymd)


def get_earliest_date(file):
    """Returns creation or modification timestamp of file

    Parameters
    ----------
    file : str
        File path

    Returns
    -------
    float
        Timestamp in seconds with microseconds as a float
    """
    # https://stackoverflow.com/questions/237079/
    # how-to-get-file-creation-modification-date-times-in-python
    if platform.system().lower() == 'windows':
        return path.getctime(file)
    else:
        st = stat(file)
        try:
            return st.st_birthtime
        except AttributeError:
            return st.st_mtime


def get_date_from_str(date_str, dt_format):
    """Returns a datetime object from a datestring of format FORMAT"""
    return datetime.strptime(date_str, dt_format)


def strip_out_date(keystring, re_format):
    """Strips out datestring of format re_format from a keystring"""
    try:
        return re.search(re_format, keystring).group()
    except AttributeError:
        logger.warning('Can\'t parse string %s for date using regex pattern '
                       '%s' % (keystring, re_format))
        return None


def get_query_resp_fstr(query_hash):
    qf = path.join(JSON_CACHE, 'query_%s.json' % query_hash)
    rf = path.join(JSON_CACHE, 'result_%s.json' % query_hash)
    return qf, rf


def list_chunk_gen(lst, size=1000):
    """Given list, generate chunks <= size"""
    n = max(1, size)
    return (lst[k:k+n] for k in range(0, len(lst), n))


def sorted_json_string(json_thing):
    """Produce a string that is unique to a json's contents."""
    if isinstance(json_thing, str):
        return json_thing
    elif isinstance(json_thing, (tuple, list)):
        return '[%s]' % (','.join(sorted(sorted_json_string(s)
                                         for s in json_thing)))
    elif isinstance(json_thing, dict):
        return '{%s}' % (','.join(sorted(k + sorted_json_string(v)
                                         for k, v in json_thing.items())))
    elif isinstance(json_thing, (int, float)):
        return str(json_thing)
    elif json_thing is None:
        return json.dumps(json_thing)
    else:
        raise TypeError('Invalid type: %s' % type(json_thing))


def get_query_hash(query_json, ignore_keys=None):
    """Create an FNV-1a 32-bit hash from the query json

    Parameters
    ----------
    query_json : dict
        A json compatible query dict
    ignore_keys : set|list
        A list or set of keys to ignore in the query_json. By default,
        no keys are ignored. Default: None.

    Returns
    -------
    int
        An FNV-1a 32-bit hash of the query json ignoring the keys in
        ignore_keys
    """
    if ignore_keys:
        if set(ignore_keys).difference(query_json.keys()):
            missing = set(ignore_keys).difference(query_json.keys())
            logger.warning(
                'Ignore key(s) "%s" are not in the provided query_json and '
                'will be skipped...' %
                str('", "'.join(missing)))
        query_json = {k: v for k, v in query_json.items()
                      if k not in ignore_keys}
    return fnv1a_32(sorted_json_string(query_json).encode('utf-8'))


def check_existence_and_date(indranet_date, fname, in_name=True):
    """With in_name True, look for a datestring in the file name, otherwise
    use the file creation date/last modification date.

    This function should return True if the file exists and is (seemingly)
    younger than the network that is currently in cache
    """
    if not path.isfile(fname):
        return False
    else:
        if in_name:
            try:
                # Try YYYYmmdd
                fdate = get_date_from_str(strip_out_date(fname, RE_YYYYMMDD),
                                          DT_YmdHMS)
            except ValueError:
                # Try YYYY-mm-dd-HH-MM-SS
                fdate = get_date_from_str(strip_out_date(fname, RE_YmdHMS_),
                                          DT_YmdHMS)
        else:
            fdate = datetime.fromtimestamp(get_earliest_date(fname))

        # If fdate is younger than indranet, we're fine
        return indranet_date < fdate


def _todays_date():
    return datetime.now().strftime('%Y%m%d')


# Copied from emmaa_service/api.py
def get_queryable_stmt_types():
    """Return Statement class names that can be used for querying."""
    def _get_sorted_descendants(cls):
        return sorted(_get_names(get_all_descendants(cls)))

    def _get_names(classes):
        return [s.__name__ for s in classes]

    stmt_types = \
        _get_names([
            Activation, Inhibition, IncreaseAmount, DecreaseAmount, Complex
        ]) + \
        _get_sorted_descendants(AddModification) + \
        _get_sorted_descendants(RemoveModification)
    return stmt_types


def load_indra_graph(dir_graph_path=None, multi_digraph_path=None,
                     sign_node_graph_path=None, sign_edge_graph_path=None,
                     update=False, belief_dict=None, strat_ev_dict=None,
                     include_entity_hierarchies=True, verbosity=0):
    """Return a nx.DiGraph and nx.MultiDiGraph representation an INDRA DB dump

    If update is True, make a fresh snapshot from the INDRA DB.
    WARNING: this typically requires a lot of RAM and might slow down your
    system significantly.
    """
    global INDRA_DG_CACHE, INDRA_MDG_CACHE, INDRA_SNG_CACHE, INDRA_SEG_CACHE
    indra_dir_graph = nx.DiGraph()
    indra_multi_digraph = nx.MultiDiGraph()
    indra_signed_edge_graph = nx.MultiDiGraph()
    indra_signed_node_graph = nx.DiGraph()

    if update:  # Todo: Download from db dumps instead
        df = make_dataframe(True, load_db_content(True, NS_LIST))
        options = {'df': df,
                   'belief_dict': belief_dict,
                   'strat_ev_dict': strat_ev_dict,
                   'include_entity_hierarchies': include_entity_hierarchies,
                   'verbosity': verbosity}
        indra_dir_graph = nf.sif_dump_df_to_digraph(**options)
        dump_it_to_pickle(dir_graph_path, indra_dir_graph)
        INDRA_DG_CACHE = path.join(CACHE, dir_graph_path)
        if multi_digraph_path:
            indra_multi_digraph = nf.sif_dump_df_to_digraph(
                graph_type='multidigraph', **options)
            dump_it_to_pickle(multi_digraph_path, indra_multi_digraph)
            INDRA_MDG_CACHE = path.join(CACHE, multi_digraph_path)
        if sign_node_graph_path or sign_edge_graph_path:
            indra_signed_edge_graph, indra_signed_node_graph = \
                nf.sif_dump_df_to_digraph(graph_type='signed', **options)
    else:
        logger.info('Loading indra network representations from pickles')
        if dir_graph_path:
            indra_dir_graph = pickle_open(dir_graph_path)
        if multi_digraph_path:
            indra_multi_digraph = pickle_open(multi_digraph_path)
        if sign_edge_graph_path:
            indra_signed_edge_graph = pickle_open(sign_edge_graph_path)
        if sign_node_graph_path:
            indra_signed_node_graph = pickle_open(sign_node_graph_path)
        logger.info('Finished loading indra networks.')
    return indra_dir_graph, indra_multi_digraph, indra_signed_edge_graph,\
        indra_signed_node_graph


def dump_query_json_to_s3(query_hash, json_obj, get_url=False):
    filename = '%s_query.json' % query_hash
    return dump_query_result_to_s3(filename, json_obj, get_url)


def dump_result_json_to_s3(query_hash, json_obj, get_url=False):
    filename = '%s_result.json' % query_hash
    return dump_query_result_to_s3(filename, json_obj, get_url)


def dump_query_result_to_s3(filename, json_obj, get_url=False):
    download_link = dump_json_to_s3(name=filename, json_obj=json_obj,
                                    public=True, get_url=get_url)
    if get_url:
        return download_link.split('?')[0]
    return None


def dump_new_nets(mdg=False, dg=False, sg=False, spbg=False, dump_to_s3=False,
                  verbosity=0, add_mesh_ids=False):
    """Main script function for dumping new networks from latest db dumps"""
    options = dict()

    if add_mesh_ids:
        df, sev, bd, mid = get_latest_sif_s3(get_mesh_ids=True)
        mid_dict = dict()
        for pair in mid:
            mid_dict.setdefault(pair[0], []).append(pair[1])
        options['mesh_id_dict'] = mid_dict
    else:
        df, sev, bd = get_latest_sif_s3()

    options.update({'df': df, 'belief_dict': bd, 'strat_ev_dict': sev,
                    'include_entity_hierarchies': True,
                    'verbosity': verbosity})

    if mdg:
        network = nf.sif_dump_df_to_digraph(graph_type='multi', **options)
        dump_it_to_pickle(INDRA_MDG_CACHE, network)
        if dump_to_s3:
            dump_pickle_to_s3(INDRA_MDG, network, prefix=NEW_NETS_PREFIX)
    if dg:
        network = nf.sif_dump_df_to_digraph(**options)
        dump_it_to_pickle(INDRA_DG_CACHE, network)
        if dump_to_s3:
            dump_pickle_to_s3(INDRA_DG, network, prefix=NEW_NETS_PREFIX)
    if sg:
        network, isng = nf.sif_dump_df_to_digraph(graph_type='signed',
                                                  **options)
        dump_it_to_pickle(INDRA_SEG_CACHE, network)
        dump_it_to_pickle(INDRA_SNG_CACHE, isng)
        if dump_to_s3:
            dump_pickle_to_s3(INDRA_SEG, network, prefix=NEW_NETS_PREFIX)
            dump_pickle_to_s3(INDRA_SNG, isng, prefix=NEW_NETS_PREFIX)

    if spbg:
        pb_seg, pb_sng = nf.sif_dump_df_to_digraph(graph_type='pybel',
                                                   **options)
        dump_it_to_pickle(INDRA_PBSNG_CACHE, pb_sng)
        dump_it_to_pickle(INDRA_PBSEG_CACHE, pb_seg)
        if dump_to_s3:
            dump_pickle_to_s3(INDRA_SNG, pb_sng, prefix=NEW_NETS_PREFIX)
            dump_pickle_to_s3(INDRA_SEG, pb_seg, prefix=NEW_NETS_PREFIX)


def find_related_hashes(mesh_ids):
    print("FIND RELATED HASHES")
    q = FromMeshIds(mesh_ids)
    result = q.get_hashes()
    return result.json().get('results', [])


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Dump new networks')
    parser.add_argument('--mdg', help='Dump a new MultiDiGraph',
                        action='store_true', default=False)
    parser.add_argument('--dg', help='Dump a new DiGraph',
                        action='store_true', default=False)
    parser.add_argument('--sg', help='Dump new signed edge and node graphs',
                        action='store_true', default=False)
    parser.add_argument('--pb', help='Dump new PyBel signed edge and node '
                                     'graphs',
                        action='store_true', default=False)
    parser.add_argument('--s3', help='Also upload the new graphs to s3',
                        action='store_true', default=False)
    args = parser.parse_args()
    dump_new_nets(mdg=args.mdg, dg=args.dg, sg=args.sg, spbg=args.pb,
                  dump_to_s3=args.s3)
