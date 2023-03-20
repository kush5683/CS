#include "manager.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

struct manager manager;
struct threadPool pool;
struct hashmap *pMap;
struct bloom_filter *bf;
struct lookupTable *lupt;
// Avoid race conditions when writing to the hashmap
pthread_mutex_t hMapMtx;
// Avoid race conditions when writing to the lookup table
pthread_mutex_t lookupTableMtx;

//* Thread function that periodically writes the hashmap to a file 
//* for persistent storage while in DISCOVERY mode
void *hashmapToFileThread(void *args)
{
    // Write out the hashmap initially
    FILE *hashmapFile;
    hashmapFile = fopen(TRUSTED_FUNCTIONS_FILE, "w");
    pthread_mutex_lock(&hMapMtx);
    writeHashmapToFile(pMap, hashmapFile);
    pthread_mutex_unlock(&hMapMtx);
    fclose(hashmapFile);
    // Loop forever
    while (1)
    {
        sleep(10);
        hashmapFile = fopen(TRUSTED_FUNCTIONS_FILE, "w");
        pthread_mutex_lock(&hMapMtx);
        writeHashmapToFile(pMap, hashmapFile);
        fclose(hashmapFile);
        pthread_mutex_unlock(&hMapMtx);
        printf("Wrote to hashmap file.\n");
    }

    fclose(hashmapFile);
}

//* Starts the manager:
//* Populate the hashmap from the txt file
//* Start the threadPool
void initManager(int maxWorkers)
{
    pthread_mutex_init(&hMapMtx, NULL);
    pthread_mutex_init(&lookupTableMtx, NULL);
    manager.numWorkers = maxWorkers;
    manager.maxWorkers = maxWorkers;
    manager.pool = &pool;
    pthread_mutex_lock(&hMapMtx);
    manager.hashmap = hashmap_initialize();

    // If FBAD mode, initialize the FBAD table
    #if INCREMENTAL_MODE
    pthread_mutex_lock(&lookupTableMtx);
    manager.lookupTable = lookupTable_initialize();

    // Otherwise, initialize the bloomfilter
    #else
    manager.bloomfilter = bloomfilter_initialize();
    #endif

    // Populate the data structures by reading in from the trusted functions file
    populateDataStructures(manager.hashmap);
    pthread_mutex_unlock(&hMapMtx);

    #if INCREMENTAL_MODE
    pthread_mutex_unlock(&lookupTableMtx);
    #endif

    // If in dynamic analysis mode, a thread to regularly write out the trusted functions to a file
    #if DISCOVERY
    pthread_t writeToFileThread;
    pthread_create(&writeToFileThread, NULL, hashmapToFileThread, NULL);
    #endif

}

//* Helper to remove leading whitespaces
char *removeLeading(char *inputStr)
{
    int idx = 0, j, k = 0;

    char *outputStr = malloc( sizeof(char) * (strlen(inputStr) + 1));
 
    // Iterate String until last
    // leading space character
    while (inputStr[idx] == ' ')
    {
        idx++;
    }
 
    // Run a for loop from index until the original
    // string ends and copy the content of str to str1
    for (j = idx; inputStr[j] != '\0'; j++)
    {
        outputStr[k] = inputStr[j];
        k++;
    }
 
    // Insert a string terminating character
    // at the end of new string
    outputStr[k] = '\0';

    return outputStr;
}

//* Populate the hashmap by reading from a dataset file
int populateDataStructures(struct hashmap *hashmap)
{
    // Read from trusted functions file
    char filepath[] = TRUSTED_FUNCTIONS_FILE;
    FILE *pFile;
    char line[600000];

    pFile = fopen(filepath, "r");
    if (pFile == NULL)
        return -1;

    #if DEBUG
    printf("Populating hashmap...\n");
    #endif

    while (fgets(line, 600000, pFile))
    { 
        // This is where all the parsing will happen
        // Parse from a file with the following format:
        // Every line is a trusted script
        // The script name is first, followed by ':'
        // Then, a space and the functions calls and their associated
        // line numbers separated by '|'. Each function call is separted by a space
        // The line ends with a tailing space then a newline

        // Ex:
        // script-name.php: fn|43 functionTwo|5342 \n

        // Each function-script relation is added to the data structures being used
        // used by Warden

        char *lookupFnName = malloc(sizeof(char) * 200);
        char *token = malloc(sizeof(char) * 200);
        char *lineno = malloc(sizeof(char) * 20);

        char *remainder, *context;

        // delimeter is ":" to get the fn name
        strcpy(lookupFnName, strtok_r(line, ":", &context));
        char *str = malloc(sizeof line / sizeof line[0]);
        strcpy(str, context);

        struct callableFunction *header = malloc(sizeof(callableFunction));
        header->name = "";
        header->next = NULL;
        header->lineno = -1;

        struct lookupScript *lfn = malloc(sizeof(struct lookupScript));
        lfn->name = lookupFnName;
        lfn->callableFunction = header;

        /* walk through callable functions*/

        strcpy(token, strtok(str, "|"));
        // Edge case where there are no functions listed,
        // Don't keep trying to parse, just set token to null and put the empty script
        // in the data structures
        if (!strcmp(token, " \n")) {
            token = NULL;
        } else {
            strcpy(lineno, strtok(NULL, " "));
        }

        while (token != NULL)
        {
            struct callableFunction *nextInList = malloc(sizeof(callableFunction));
            nextInList->name = removeLeading(token);
            nextInList->next = NULL;
            nextInList->lineno = atoi(lineno);

            struct callableFunction *curr = lfn->callableFunction;
            while (curr->next)
            {
                curr = curr->next;
            }
            if (curr->name == "") // Replace the header
            {
                *curr = *nextInList;
            }
            else
            {
                curr->next = nextInList;
            }

            char *next_func = strtok(NULL, "|");
            char *next_lineno = strtok(NULL, " ");

            if (next_func == NULL || *next_func == '\n')
            {
                break;
            }

            token = next_func;
            lineno = next_lineno;
        }

        // add the lookup function to the hashmap
        // Remove header if it is there
        if(lfn->callableFunction->lineno == -1) {
            lfn->callableFunction = NULL;
        }
        hashmap_set(manager.hashmap, lfn);

        // Adding script-function relation to bloom filter
        struct callableFunction *curr = lfn->callableFunction;
        while (curr)
        {
    #if INCREMENTAL_MODE // FBAD Table
            char *key = malloc(sizeof(char) * (strlen(lfn->name) + 1));
            memset(key, 0, sizeof(char) * (strlen(lfn->name) + 1));
            strcat(key, lfn->name);
            char *entry = malloc(sizeof(char) * (strlen(curr->name) + 1));
            memset(entry, 0, sizeof(char) * (strlen(curr->name) + 1));
            strcat(entry, curr->name);
            incrementFunctionCall(manager.lookupTable, key, entry, curr->lineno);
    #else // Bloom Filter
            char *key = malloc(sizeof(char) * (strlen(lfn->name) + strlen(curr->name) + 22));
            memset(key, 0, sizeof(char) * (strlen(lfn->name) + strlen(curr->name) + 22));
            strcat(key, lfn->name);
            strcat(key, ":");
            strcat(key, curr->name);
            char stringLineno[20];
            sprintf(stringLineno, "%d", curr->lineno);
            strcat(key, stringLineno);
            put_bloom_filter(manager.bloomfilter, key);
            free(key);
    #endif
            curr = curr->next;
        }

    #if DEBUG
        printf("Added function to hashmap...\n");
    #endif
    }

    return 0;
}

//* Print out WARDEN configuration info
void printWARDENConfig() {
    
    char lightweightCFI[500];
    char *modeOfOperation;
    
#if INCREMENTAL_MODE
    sprintf(lightweightCFI, "Incremental Filter\n\tTrust Threshold: %d", NUM_TRUSTED_OCCURENCES);
#else 
    sprintf(lightweightCFI, "Bloom Filter\n\tSize: %ld\n\tHash Functions: %ld", bf->bit_array->number_bits, bf->num_functions);
#endif
#if DISCOVERY
    modeOfOperation = "Discovery Mode";
#else 
    modeOfOperation = "Enforcement Mode";
#endif

    printf("----- WARDEN Configuration: -----\n\n- Mode of Operation: %s\n- Lightweight CFI: %s\n- # CFI Worker Threads: %d\n- DEBUG Mode: %d\n- Record PHP Logs: %d\n- CFI Threat Log File Path: %s\n- WARDEN Log File Path: %s\n- WP Source Code Directory: %s\n- PHP Functions Log File Path: %s\n\n", modeOfOperation, lightweightCFI, NUM_CFI_WORKER_THREADS, DEBUG, WRITE_LOGS_TO_FILE, CFI_LOG_FILE, WARDEN_LOG_FILE, WORDPRESS_DIRECTORY, PARSED_LOG_FILE_PATH);

}

//* Entry point for Warden
int main(int argc, char const *argv[])
{
    initManager(NUM_CFI_WORKER_THREADS);
    #if DEBUG
    printMap(manager.hashmap);
    #endif
    // sets up the server for parsing incoming logs
    initialize_parsing_structs();
    // print out WARDEN configuration info
    printWARDENConfig();
    // start the server
    runSocketParsing();
    // start the threadpool which has threads to run the CFI
    initThreadPool(manager.maxWorkers);
    return 0;
}