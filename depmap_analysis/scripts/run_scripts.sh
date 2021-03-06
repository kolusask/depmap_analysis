# Set the following environment variables:
# OUTDIR : the output directory
# DATA_DIR : where the inpup depmap data is
# SIF_DIR : where the DB dumps are
# Remember to check the mu sigma values for any new depmap dataset

cmu=0.003076; csig=0.056813;
rmu=0.006854; rsig=0.077614;

lw_sif=db_dump_df_lite_hgnc_fplx_curated.csv

ll=5; ul='';
echo "Running $ll-$ul SD"
echo "Output goes to ${OUTDIR}/${ll}_${ul}sd/"
python depmap_script.py -cf "${DATA_DIR}/19Q4/Achilles_gene_effect.csv" -cc "${DATA_DIR}/19Q4/_crispr_all_correlations.h5"\
  -rf "${DATA_DIR}/demeter/D2_combined_gene_dep_scores.csv" -rc "${DATA_DIR}/demeter/_rnai_all_correlations.h5"\
  -b "${SIF_DIR}/belief_dict.pkl" --filter-type None --no-web-files\
  --hgnc-name2id "${SIF_DIR}/hgnc_name2id.pkl" --fplx-name2id "${SIF_DIR}/fplx_name2id.pkl"\
  --explained-set "${DATA_DIR}/gene_sets/mito_function_depmap.csv" gene\
  -lw "${SIF_DIR}/${lw_sif}" -cstats $cmu $csig -rstats $rmu $rsig -crange $ll $ul -rrange $ll $ul\
  -o "${OUTDIR}/${ll}_${ul}sd/" > "${OUTDIR}/${ll}_${ul}sd/stout.log"
echo "Finished running $ll-$ul SD"

ll=4; ul=5;
echo "Running $ll-$ul SD"
echo "Output goes to ${OUTDIR}/${ll}_${ul}sd/"
python depmap_script.py -cf "${DATA_DIR}/19Q4/Achilles_gene_effect.csv" -cc "${DATA_DIR}/19Q4/_crispr_all_correlations.h5"\
  -rf "${DATA_DIR}/demeter/D2_combined_gene_dep_scores.csv" -rc "${DATA_DIR}/demeter/_rnai_all_correlations.h5"\
  -b "${SIF_DIR}/belief_dict.pkl" --filter-type None --no-web-files\
  --hgnc-name2id "${SIF_DIR}/hgnc_name2id.pkl" --fplx-name2id "${SIF_DIR}/fplx_name2id.pkl"\
  --explained-set "${DATA_DIR}/gene_sets/mito_function_depmap.csv" gene\
  -lw "${SIF_DIR}/${lw_sif}" -cstats $cmu $csig -rstats $rmu $rsig -crange $ll $ul -rrange $ll $ul\
  -o "${OUTDIR}/${ll}_${ul}sd/" > "${OUTDIR}/${ll}_${ul}sd/stout.log"
echo "Finished running $ll-$ul SD"

ll=3; ul=4;
echo "Running $ll-$ul SD"
echo "Output goes to ${OUTDIR}/${ll}_${ul}sd/"
python depmap_script.py -cf "${DATA_DIR}/19Q4/Achilles_gene_effect.csv" -cc "${DATA_DIR}/19Q4/_crispr_all_correlations.h5"\
  -rf "${DATA_DIR}/demeter/D2_combined_gene_dep_scores.csv" -rc "${DATA_DIR}/demeter/_rnai_all_correlations.h5"\
  -b "${SIF_DIR}/belief_dict.pkl" --filter-type None --no-web-files\
  --hgnc-name2id "${SIF_DIR}/hgnc_name2id.pkl" --fplx-name2id "${SIF_DIR}/fplx_name2id.pkl"\
  --explained-set "${DATA_DIR}/gene_sets/mito_function_depmap.csv" gene\
  -lw "${SIF_DIR}/${lw_sif}" -cstats $cmu $csig -rstats $rmu $rsig -crange $ll $ul -rrange $ll $ul\
  -o "${OUTDIR}/${ll}_${ul}sd/" > "${OUTDIR}/${ll}_${ul}sd/stout.log"
echo "Finished running $ll-$ul SD"

ll=2; ul=3;
echo "Running $ll-$ul SD"
echo "Output goes to ${OUTDIR}/${ll}_${ul}sd/"
python depmap_script.py -cf "${DATA_DIR}/19Q4/Achilles_gene_effect.csv" -cc "${DATA_DIR}/19Q4/_crispr_all_correlations.h5"\
  -rf "${DATA_DIR}/demeter/D2_combined_gene_dep_scores.csv" -rc "${DATA_DIR}/demeter/_rnai_all_correlations.h5"\
  -b "${SIF_DIR}/belief_dict.pkl" --filter-type None --no-web-files\
  --hgnc-name2id "${SIF_DIR}/hgnc_name2id.pkl" --fplx-name2id "${SIF_DIR}/fplx_name2id.pkl"\
  --explained-set "${DATA_DIR}/gene_sets/mito_function_depmap.csv" gene\
  -lw "${SIF_DIR}/${lw_sif}" -cstats $cmu $csig -rstats $rmu $rsig -crange $ll $ul -rrange $ll $ul\
  -o "${OUTDIR}/${ll}_${ul}sd/" > "${OUTDIR}/${ll}_${ul}sd/stout.log"
echo "Finished running $ll-$ul SD"

ll=1; ul=2;
echo "Running $ll-$ul SD"
echo "Output goes to ${OUTDIR}/${ll}_${ul}sd/"
python depmap_script.py -cf "${DATA_DIR}/19Q4/Achilles_gene_effect.csv" -cc "${DATA_DIR}/19Q4/_crispr_all_correlations.h5"\
  -rf "${DATA_DIR}/demeter/D2_combined_gene_dep_scores.csv" -rc "${DATA_DIR}/demeter/_rnai_all_correlations.h5"\
  -b "${SIF_DIR}/belief_dict.pkl" --filter-type None --no-web-files\
  --hgnc-name2id "${SIF_DIR}/hgnc_name2id.pkl" --fplx-name2id "${SIF_DIR}/fplx_name2id.pkl"\
  --explained-set "${DATA_DIR}/gene_sets/mito_function_depmap.csv" gene\
  -lw "${SIF_DIR}/${lw_sif}" -cstats $cmu $csig -rstats $rmu $rsig -crange $ll $ul -rrange $ll $ul\
  -o "${OUTDIR}/${ll}_${ul}sd/" > "${OUTDIR}/${ll}_${ul}sd/stout.log"
echo "Finished running $ll-$ul SD"
