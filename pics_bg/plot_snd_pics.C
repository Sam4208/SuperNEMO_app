#include "/sps/nemo/scratch/spratt/analysis/running_files/analysis_functions.C"






int main (int argc, char *argv[])
{


	open_file_UDD("/sps/nemo/snemo/snemo_data/reco_data/UDD/delta-tdc-10us-v3/snemo_run-1295_udd.root");
	for (int i = 1; i <= 5000; ++i) {
	save_event_UDD(i,"1295_");}

	return 1;

}

