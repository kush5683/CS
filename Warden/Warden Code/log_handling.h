#include "CFI_CONFIG.h"

// Unused enum for type of assignment a thread will look at
typedef enum
{
    Weak,
    Strong,
    None
} assignmentType;

/* Linked list of unparsed logs */
typedef struct unparsed_log
{
    char type;
    long long msg_len;
    char msg_bodybuffer[BUFFER_SIZE];
    struct unparsed_log *next;
} unparsed_log;

/* The queue of unparsed logs, with size, head, tail, and mutex */
typedef struct unparsed_queue
{
    size_t queue_size;
    unparsed_log *head;
    unparsed_log *tail;
    pthread_mutex_t mtx;
    pthread_cond_t cond;
} unparsed_queue;

/* Struct of a parsed log (type 1 or 3) */
typedef struct parsed_log
{
    char type;
    long long msg_len;
    long long timestamp;
    char *npfcookie;
    char ip_1;
    char ip_2;
    char ip_3;
    char ip_4;
    int lineno;
    long long script_name_len;
    char *script_name;
    long long class_name_len;
    char *class_name;
    long long function_name_len;
    char *function_name;
    long long param_len;
    char *param;
    struct parsed_log *next;

} parsed_log;

/* The queue of parsed logs. */
struct parsed_queue
{
    size_t queue_size;
    parsed_log *head;
    parsed_log *tail;
    pthread_mutex_t mtx;
    pthread_cond_t cond;
};

// ----------------------------------------------------- FUNCTIONS  ----------------------------------------------------- //

extern void print_unp_log(struct unparsed_log unplog);
extern void print_parsed_log(struct parsed_log plog);
extern int add_to_unparsed_queue(struct unparsed_log unplog);
extern int add_to_parsed_queue(struct parsed_log *plog);
extern void initialize_parsing_structs();

extern void *read_logs_thread(void *args);
extern void *read_from_socket(void *args);
void *handleClient(void *socket);
