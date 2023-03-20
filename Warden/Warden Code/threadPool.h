#include <pthread.h>
#include <string.h>
#include "log_handling.h"
#include "incremental_filter.h"
#include "hashmap.h"
#include "bloomfilter.h"
#include "CFI_CONFIG.h"

// Manager struct to track global variables
struct manager
{
    int numWorkers;
    int maxWorkers;
    struct threadPool *pool;
    struct hashmap *hashmap;
    struct bloom_filter *bloomfilter;
    struct lookupTable *lookupTable;
};

// CFI Worker Thread Struct
struct worker
{
    pthread_t thread;
    int thread_id;
    assignmentType assignmentType;
    struct parsed_log *assignment;
    pthread_mutex_t mtx;
};

// Pool of CFI Workers
struct threadPool
{
    struct worker *head;
    int numWorkers;
    int maxWorkers;
    pthread_mutex_t mtx;
};

// Define External Variables
extern struct manager manager;
extern struct threadPool pool;
extern pthread_mutex_t hMapMtx;

// Function Signatures
extern int initThreadPool(int maxWorkers);
extern int runSocketParsing();
int strongCFI(void *args);
int weakCFI(void *args);
void *runWorker(void *args);
struct parsed_log *grabSomethingFromTheQ();