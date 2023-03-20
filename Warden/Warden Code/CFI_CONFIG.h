
// ------------------------------------------ Filepaths ------------------------------------------ //
#define CFI_LOG_FILE "/home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/CFI_Threat.log"
#define WARDEN_LOG_FILE "/home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/warden.log"
#define STATIC_ANALYSIS_FILE "/home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/static analysis/functions-line-num.txt"
#define TRUSTED_FUNCTIONS_FILE "/home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/trustedFunctions.txt"
#define WORDPRESS_DIRECTORY "/home/student/sus-stuff/mqp_sus_history/sus-manager/wp-versions/wp-511-ubuntu/nginx-fpm-build/wordpress"
#define PARSED_LOG_FILE_PATH "/home/student/sus-stuff/mqp_sus_history/sus-manager/CFI/wp_logs.txt"

// ------------------------------------------ MODES OF OPERATION ------------------------------------------ //
#define DEBUG 0
// If we are in DISCOVERY learning mode where all function transfers will be added as valid
// to the hashmap
#define DISCOVERY 0
// Writes parsed logs to PARSED_LOG_FILE_PATH as the parsing server parses them
#define WRITE_LOGS_TO_FILE 0
// If in INCREMENTAL_MODE, the lightweight CFI method used will be the lookup table, otherwise use bloom filter
#define INCREMENTAL_MODE 0

// ------------------------------------------ Log handling constants ------------------------------------------ //

//Port to recive unparsed logs from the container
#define PORT 10123
// Buffer size to read unparsed logs from container
#define BUFFER_SIZE 1024
// Message offsets from unparsed logs
#define IP_OFFSET 40
#define LINENO_OFFSET 44
#define SCRIPT_NAME_LEN_OFFSET 48
#define SCRIPT_NAME_OFFSET 56


// ------------------------------------------ CFI Operating Parameters ------------------------------------------ //

// Number of occurences needed for the lookup table to trust a function call
#define NUM_TRUSTED_OCCURENCES 5
// Number of CFI worker threads that Warden will create in its threadpool
#define NUM_CFI_WORKER_THREADS 20


