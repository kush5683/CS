#include "threadPool.h"
#include <stdio.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <dirent.h>

// Parsed Log Queue
struct parsed_queue p_queue;
// Unparsed Log Queue
struct unparsed_queue unp_queue;
// Empty parsed and unparsed log structs used to instantiate the queue
struct parsed_log nullPLog;
struct unparsed_log nullUnpLog;

// Hashmap Mutex
extern pthread_mutex_t hMapMtx;
// Used in Frequency-Based Anomaly Detection Mode, FBAD Mutex
extern pthread_mutex_t lookupTableMtx;

//* Debugging function that prints the parsed log queue to p_queue.txt
void checkParsedLogQueue()
{
    sleep(10);
    for (;;)
    {
        pthread_mutex_lock(&p_queue.mtx);
        struct parsed_log *a = p_queue.head;
        
        FILE *write_File;
        write_File = fopen("p_queue.txt", "w+");
        // fprintf(write_File, "Plog: %p\tFunc: %p %s\tScript: %p %s\t\n\n", p_queue.head, p_queue.head->function_name, p_queue.head->function_name, p_queue.head->script_name, p_queue.head->script_name);
        // fprintf(write_File, "Plog: %p\tFunc: %p %s\tScript: %p %s\t\n\n", p_queue.head->next, p_queue.head->next->function_name, p_queue.head->next->function_name, p_queue.head->next->script_name, p_queue.head->next->script_name);
        // fprintf(write_File, "Plog: %p\tFunc: %p %s\tScript: %p %s\t\n\n", p_queue.head->next->next, p_queue.head->next->next->function_name, p_queue.head->next->next->function_name, p_queue.head->next->next->script_name, p_queue.head->next->next->script_name);
        while(a->next){
            fprintf(write_File, "Plog: %p\tFunc: %p %s\tScript: %p %s\t\n\n", a, a->function_name, a->function_name, a->script_name, a->script_name);
            a = a->next;
        }
        fclose(write_File);

        pthread_mutex_unlock(&p_queue.mtx);
        printf("wrote\n");
        sleep(10);
    }
}

//* Initialize the manager and the thread pool
extern int initThreadPool(int maxWorkers)
{
    pool.head = malloc(sizeof(struct worker) * manager.maxWorkers);
    for (int i = 0; i < manager.maxWorkers; i++)
    {
        pthread_t thread;
        pthread_mutex_t worker_mtx;
        pool.head[i] = (struct worker){thread, i, Weak, NULL, worker_mtx};
        pthread_create(&pool.head[i].thread, NULL, runWorker, &pool.head[i]);
        // runWorker(&pool.head[i]);
    }
    for (int i = 0; i < manager.maxWorkers; i++)
    {
        pthread_join(pool.head[i].thread, NULL);
    }

    return 0;
}

//* Run a CFI worker thread. args: The worker thread that is being run
void *runWorker(void *args)
{
    // Get the worker struct passed in as an argument
    struct worker *w = (struct worker *)args;
    #if DEBUG
    printf("I am worker %d \n", w->thread_id);
    #endif
    for (;;)
    {  
        // Remove a log from the queue
        struct parsed_log *plog = grabSomethingFromTheQ();
        w->assignment = plog;

    // If in Discovery Mode, add the function call the the trusted set
    #if DISCOVERY
        pthread_mutex_lock(&hMapMtx);
        addFromLogInfo(manager.hashmap, plog->script_name, plog->function_name, plog->lineno);
        pthread_mutex_unlock(&hMapMtx);
    #endif

    // If in CFI Mode
    #if !DISCOVERY
        // Run "weak" (bloom filter) CFI
        if(!weakCFI(w))
        {
            // If weakCFI finds the log suspicious, elevate it to strongCFI (hashmap CFI)
            strongCFI(w);
        }
        // Free the log structure
        free(plog->function_name);
        free(plog->script_name);
        free(plog);
    #endif
    }

    return NULL;
}

//* Start the socket reading and parsing threads to catch logs from the PHP extension
//* runs code from server.c
extern int runSocketParsing()
{
    pthread_t socketParsingThread;
    pthread_create(&socketParsingThread, NULL, read_from_socket, NULL);
    return 0;
}

//* Remove a log from the queue and return it
struct parsed_log *grabSomethingFromTheQ()
{
    for (;;)
    {
        // Check if the queue has anything in it
        pthread_mutex_lock(&p_queue.mtx);
        while (p_queue.queue_size == 0 || p_queue.head->function_name == NULL)
        {
            // If it doesn't, halt until the parsing process broadcasts that there is something in the queue
            pthread_cond_wait(&p_queue.cond, &p_queue.mtx);
            continue;
        }

        // Remove a log from the queue
        struct parsed_log *a = p_queue.head;
        // Reassign the head of the queue to the next log
        p_queue.head = a->next;
        // Update the queue size
        p_queue.queue_size--;

        // Release the mutex
        pthread_mutex_unlock(&p_queue.mtx);
        // Change the removed log's "next" attribute to NULL
        a->next = NULL;
        // Return the removed log
        return a;
    }
}

//* Helper to get the string form of an IP address from a log
//* Uses the arpa/inet.h library
char *getIPFromLog(struct parsed_log *log)
{
    char ipFull[4];
    ipFull[3] = log->ip_4;
    ipFull[2] = log->ip_3;
    ipFull[1] = log->ip_2;
    ipFull[0] = log->ip_1;
    uint32_t ip = *((uint32_t *)ipFull);
    struct in_addr ip_addr;
    ip_addr.s_addr = ip;
    return inet_ntoa(ip_addr);
}

//* Helper that is called when a script-function relation is not found in the hashmap
//* Checks the log's validity by analyzing source code ad hoc
//* Will ensure the script exists and that the function is called on the right lineno
int investigateUnknownLog(struct parsed_log *log)
{
    // Get all the relevant info from the log
    char *scriptName = log->script_name;
    char *functionName = log->function_name;
    int lineno = log->lineno;
    // Path to the server source code
    char *startingPath = WORDPRESS_DIRECTORY;

    // Determine if script exists by trying to open it
    char *scriptPath = malloc(1000);
    memset(scriptPath, 0, sizeof(scriptPath));
    strcat(scriptPath, startingPath);
    strcat(scriptPath, "/");
    strcat(scriptPath, log->script_name);
    FILE *scriptFile;

    scriptFile = fopen(scriptPath, "r");

    // If we can't open the file then it doesn't exist
    if (scriptFile == NULL)
    {
        // Free the scriptPath buffer
        free(scriptPath);
        return 0;
    }
    // Check if function exists in script at the line number
    int currentLineNum = 1;
    // Buffer to hold the line
    char line[1000];
    // Read line by line
    while (fgets(line, sizeof(line), scriptFile) != NULL)
    {
        if (currentLineNum == lineno)
        {
            char *indexOfFunction = strstr(line, functionName);
            // If the function was not found at the line then the log is not valid
            if (indexOfFunction == NULL)
            {
                // Free the FILE* and the buffer
                fflush(scriptFile);
                fclose(scriptFile);
                free(scriptPath);
                return 0;
            }
        }
        currentLineNum++;
    }
    // If line number is out of range of the script, the log is invalid
    if (lineno < 1 || currentLineNum < lineno)
    {
        // Free the FILE* and the buffer
        fflush(scriptFile);
        fclose(scriptFile);
        free(scriptPath);
        return 0;
    }

    // Free the FILE* and the buffer
    fflush(scriptFile);
    fclose(scriptFile);
    free(scriptPath);
    // If we get here, it has passed all tests, so the log is valid
    return 1;
}

//* Helper that updates the hashmap and bloom filter/FBAD table when a log is found to be legitimate
void updateDataStructures(struct parsed_log *log) {

    // Get relevant log info
    char *script_name = log->script_name;
    char *function_name = log->function_name;
    int lineno = log->lineno;

    // Update the hashmap
    addFromLogInfo(manager.hashmap, script_name, function_name, lineno);

    #if INCREMENTAL_MODE
    // Update the FBAD table
    pthread_mutex_lock(&lookupTableMtx);
    incrementFunctionCall(manager.lookupTable, script_name, function_name, lineno);
    pthread_mutex_unlock(&lookupTableMtx);

    #else    
    // Update the bloom filter
    char *key = malloc(sizeof(char) * (strlen(function_name) + strlen(script_name) + 22));
    // Construct the key to follow the format - script:function:lineno
    memset(key, 0, sizeof(char) * (strlen(function_name) + strlen(script_name) + 22));
    strcat(key, script_name);
    strcat(key, ":");
    strcat(key, function_name);
    char stringLineno[20];
    sprintf(stringLineno, "%d", lineno);
    strcat(key, stringLineno);
    // Add the new function call to the bloom filter
    put_bloom_filter(manager.bloomfilter, key);
    // Free the key buffer
    free(key);
#endif

    // Log that a new function was added to the trusted set
    FILE *fp = fopen(WARDEN_LOG_FILE, "a");
    fprintf(fp, "[HASH. CFI]: Script-Function Added -\n\tContainer IP: %s\n\tFn: %s\n\tScript: %s\n\tLineno: %d\n\tTimestamp of Call: %lld\n\n", getIPFromLog(log), function_name, script_name, log->lineno, log->timestamp);
    fclose(fp);
}

//* The "strong" CFI, a.k.a. hashmap CFI
int strongCFI(void *args)
{
    // Used to investigate log is found in the hashmap
    int isValid;

    // Parse the argument to a worker
    struct worker *w = (struct worker *)args;

    // Extract important variables
    struct parsed_log *log = w->assignment;
    char *script_name = log->script_name;
    char *function_name = log->function_name;
    int lineno = log->lineno;

    // Lock the hashmap mutex
    pthread_mutex_lock(&hMapMtx);
    // Try to get script from hashmap
    struct lookupScript *bucket = hashmap_get(manager.hashmap, script_name);

    // If script is not in hashmap
    if (bucket == NULL)
    {
        // Check if the script exists and has the function called
        isValid = investigateUnknownLog(w->assignment);

        // If so, add it to the data structures and unlock the mutex
        if (isValid)
        {
            updateDataStructures(w->assignment);
            pthread_mutex_unlock(&hMapMtx);
        }
        // If not, log the illegal script call and unlock the mutex
        else
        {
            pthread_mutex_unlock(&hMapMtx);
            FILE *fp = fopen(CFI_LOG_FILE, "a");
            fprintf(fp, "[HASH. CFI]: Script not Found -\n\tContainer IP: %s\n\tScript: %s\n\tLineno: %d\n\tTimestamp of Call: %lld\n\n", getIPFromLog(log), script_name, log->lineno, log->timestamp);
            fclose(fp);
        }
        return isValid;
    }

    // After determining the script exists, step through allowed functions and see if ours is in there
    callableFunction *current = bucket->callableFunction;
    while (current != NULL)
    {
        // If the script-function relation is in hashmap, unlock mutex, update data structures and return 1
        if ((strcmp(current->name, function_name) == 0) && (lineno == current->lineno))
        {
            updateDataStructures(w->assignment);
            pthread_mutex_unlock(&hMapMtx);
            return 1;
        }
        current = current->next;
    }

    // If the script-function relation is not in hashmap,
    // check if it is valid and we just haven't caught it before
    isValid = investigateUnknownLog(w->assignment);

    // If it is, add it to the data structures and unlock the mtx
    if (isValid)
    {
        updateDataStructures(w->assignment);
        pthread_mutex_unlock(&hMapMtx);
    }
    // If not, unlock the mutex and log the illegal function call
    else
    {
        pthread_mutex_unlock(&hMapMtx);
        FILE *fp = fopen(CFI_LOG_FILE, "a");
        fprintf(fp, "[HASH. CFI]: Illegal Function Call -\n\tContainer IP: %s\n\tFn: %s\n\tScript: %s\n\tLineno: %d\n\tTimestamp of Call: %lld\n\n", getIPFromLog(log), function_name, script_name, log->lineno, log->timestamp);
        fclose(fp);
    }

    // Return if it was valid or not
    return isValid;
}

//* The "weak" CFI< a.k.a. bloomfilter or lightweight CFI
int weakCFI(void *args)
{
    // Parse the worker struct from the args
    struct worker *w = (struct worker *)args;

    // Get the important values from the worker
    struct parsed_log *log = w->assignment;
    char *script_name = log->script_name;
    char *function_name = log->function_name;
    int lineno = log->lineno;

    // If in FBAD mode
    #if INCREMENTAL_MODE
    pthread_mutex_lock(&lookupTableMtx);
    // Check if function has been seen >= NUM_TRUSTED_OCCURENCES times
    int isValid = lookupTable_query(manager.lookupTable, script_name, function_name, lineno);
    pthread_mutex_unlock(&lookupTableMtx);
    return isValid;

    // If in Bloom Filter mode
    #else
    char key[1000] = {0x00};
    // Construct key with format - script:function:lineno
    strcat(key, script_name);
    strcat(key, ":");
    strcat(key, function_name);
    char stringLineno[20];
    sprintf(stringLineno, "%d", lineno);
    strcat(key, stringLineno);
    // Check if the function call is in the bloom filter
    int isValid = check_if_in_bloom_filter(manager.bloomfilter, key);
    return isValid;
    #endif
}