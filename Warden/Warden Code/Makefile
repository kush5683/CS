warden:  manager.c threadPool.c hashmap.c server.c bloomfilter.c
	gcc -O3 manager.c threadPool.c hashmap.c server.c bloomfilter.c incremental_filter.c -lm -o warden -pthread

clean:
		rm -f warden manager server threadPool strongCFI.log incremental_filter_printout.txt CFI_Threat.log warden.log wp_logs.txt
