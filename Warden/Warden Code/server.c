#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <time.h>
#include <pthread.h>
#include <sys/wait.h>
#include <execinfo.h>
#include <execinfo.h>
#include <signal.h>
#include "log_handling.h"

// ----------------------------------------------------- GLOBAL INITIALIZATIONS  ----------------------------------------------------- //

// Used to make the starting pointers in unp_queue and unparsed_log entries
extern struct unparsed_log nullUnpLog;
extern struct parsed_log nullPLog;

// Instantiate the unparsed queue
extern struct unparsed_queue unp_queue;

// Instantiate the parsed queueS
extern struct parsed_queue p_queue;

// ----------------------------------------------------- HELPER FUNCTIONS ----------------------------------------------------- //

//* Helper to initialize global unparsed queue and parsed queue
extern void initialize_parsing_structs()
{
    pthread_cond_init(&unp_queue.cond, NULL);
    unp_queue.head = &nullUnpLog;
    unp_queue.tail = &nullUnpLog;

    pthread_cond_init(&p_queue.cond, NULL); 
    p_queue.queue_size = 0;
    p_queue.head = &nullPLog;
    p_queue.tail = &nullPLog;
}

//* Helper to print unparsed logs
//* unplog : The unparsed log to print
extern void print_unp_log(struct unparsed_log unplog)
{
    printf("Type: %d\n", unplog.type);
    printf("Msg_len: %lld\n", unplog.msg_len);
    printf("Size of buffer: %ld\n\n", sizeof(unplog.msg_bodybuffer));
}

//* Helper to print parsed logs
//* plog : The parsed log to print
extern void print_parsed_log(struct parsed_log plog)
{
    printf("Type: %x\n", plog.type);
    printf("Timestamp: %lld\n", plog.timestamp);
    printf("Message length: %lld\n", plog.msg_len);
    printf("IP: %hhu.%hhu.%hhu.%hhu\n", plog.ip_1, plog.ip_2, plog.ip_3, plog.ip_4);
    printf("Line no: %d\n", plog.lineno);
    printf("Script name length: %lld\n", plog.script_name_len);
    printf("Script name: %s\n", plog.script_name);
    printf("Class name length: %lld\n", plog.class_name_len);
    printf("Class name: %s\n", plog.class_name);
    printf("Function name length: %lld\n", plog.function_name_len);
    printf("Function name: %s\n", plog.function_name);
    printf("Param length: %lld\n", plog.param_len);
    printf("Param: %s\n", plog.param);
    printf("--------------------------\n");
}

//* Helper that adds an unparsed_queue to the unparsed queue
//* unplog : The parsed log to add to the unparsed queue
extern int add_to_unparsed_queue(struct unparsed_log unplog)
{
    // Queue is empty
    if (unp_queue.queue_size == 0)
    {
        // Add as head and tail
        *unp_queue.head = unplog;
        *unp_queue.tail = unplog;
        unp_queue.queue_size += 1;
        pthread_mutex_unlock(&unp_queue.mtx);
        return 0;
    }
    // Queue has items
    else if (unp_queue.queue_size > 0)
    {
        // Update tail's next
        *unp_queue.tail->next = unplog;
        // Add as tail
        *unp_queue.tail = unplog;
    }
    unp_queue.queue_size += 1;
    // This function should only be called when the caller has grabbed the mutex, so release the mutex.
    // If we have reached our threshold, wake the parsing thread
    int wakeWorkers = (unp_queue.queue_size >= 10000);
    pthread_mutex_unlock(&unp_queue.mtx);
    if (wakeWorkers) {
        pthread_cond_broadcast(&unp_queue.cond);
    }
    return 0;
}

//* Helper that adds a parsed_queue to the parsed queue
//* plog : The parsed log to add to the parsed queue
extern int add_to_parsed_queue(struct parsed_log *plog)
{

    // Queue is empty
    if (p_queue.queue_size == 0 || p_queue.head->function_name == NULL)
    {
        // Add as head and tail
        p_queue.head = plog;
        p_queue.tail = plog;
        p_queue.queue_size += 1;
        pthread_mutex_unlock(&p_queue.mtx);
        return 0;
    }
    // Queue has items
    else if (unp_queue.queue_size > 0)
    {
        // Update tail's next
        p_queue.tail->next = plog;
        // Add as tail
        p_queue.tail = plog;
    }

    p_queue.queue_size += 1;
    // This function should only be called when the caller has grabbed the mutex, so release the mutex.
    // If we have reached our threshold, wake all the CFI worker threads.
    int wakeWorkers = (p_queue.queue_size >= 10000);
    pthread_mutex_unlock(&p_queue.mtx);
    if (wakeWorkers) {
        pthread_cond_broadcast(&p_queue.cond);
    }
    return 0;
}

//* Helper that writes parsed log to file
//* logFile : The file pointer that will be written to
//* parsed_log : The parsed log that will be written
extern void write_parsed_log_to_file(FILE *logFile, struct parsed_log parsed_log)
{
    // Write log to file (throw into a queue for CFI later)
    fprintf(logFile, "Type:\t%x\n", parsed_log.type);
    fprintf(logFile, "Timestamp:\t%lld\n", parsed_log.timestamp);
    fprintf(logFile, "IP:\t%hhu.%hhu.%hhu.%hhu\n", parsed_log.ip_1, parsed_log.ip_2, parsed_log.ip_3, parsed_log.ip_4);
    fprintf(logFile, "Line no:\t%d\n", parsed_log.lineno);
    fprintf(logFile, "Script name:\t%s\n", parsed_log.script_name);
    fprintf(logFile, "Class name:\t%s\n", parsed_log.class_name);
    fprintf(logFile, "Function name:\t%s\n", parsed_log.function_name);
    fprintf(logFile, "Param:\t%s\n", parsed_log.param);
    fprintf(logFile, "--------------------------\n");
    fflush(logFile);
}

// ----------------------------------------------------- LOG PARSING THREAD ----------------------------------------------------- //

//* Thread that will read from the queue of unparsed logs and parse them,
//* then add them to the parsed queue
extern void *read_logs_thread(void *args)
{
    // Local variable to store our unparsed log
    unparsed_log current_log;

    #if WRITE_LOGS_TO_FILE
    FILE *logFile;
    logFile = fopen(PARSED_LOG_FILE_PATH, "a+");
    #endif

    // Infinite loop
    for (;;)
    {

        parsed_log *parsed_log = malloc(sizeof(struct parsed_log));
        memset(parsed_log, 0x00, sizeof(struct parsed_log));

        // Grab mutex
        pthread_mutex_lock(&unp_queue.mtx);
        // Wait until there is something in unparsed_queue
        while (unp_queue.queue_size == 0)
        {
            // If it is empty, halt until the unparsed log thread broadcasts to wake up
            pthread_cond_wait(&unp_queue.cond, &unp_queue.mtx);
            continue;
        }
        // Take the first thing
        current_log = *unp_queue.head;
        // Set the queue head to the new head of the list
        unp_queue.head = current_log.next;
        // Decrement the queue size
        unp_queue.queue_size -= 1;
        // Release mutex
        pthread_mutex_unlock(&unp_queue.mtx);

        // Set our extracted log's next value to NULL
        current_log.next = NULL;

        // Get buffer of current log (save to variable to make code prettier)
        char buffer[BUFFER_SIZE] = {0x00};
        memcpy(buffer, current_log.msg_bodybuffer, sizeof(current_log.msg_bodybuffer));

        // Fill in fields that are shared between Types 1 and 3
        parsed_log->type = current_log.type;

        parsed_log->timestamp = *((long long *)(buffer));

        //  Exit if the log is malformed.
        // This error is still unresolved. For some reasons some logs appear malformed and must be thrown out
        // Future work could resolve this issue when they try to improve the log exfiltration method
        if (parsed_log->timestamp < 1000000000000 || parsed_log->timestamp > 3000000000000)
        {
            printf("[PARSING THREAD] Got malformed log. Timestamp: %lld\n", parsed_log->timestamp);
            continue;
        }

        // Parse log fields
        parsed_log->ip_1 = *((char *)(buffer + IP_OFFSET));
        parsed_log->ip_2 = *((char *)(buffer + IP_OFFSET + 1));
        parsed_log->ip_3 = *((char *)(buffer + IP_OFFSET + 2));
        parsed_log->ip_4 = *((char *)(buffer + IP_OFFSET + 3));
        parsed_log->lineno = *((int *)(buffer + LINENO_OFFSET));
        parsed_log->script_name_len = *((long long *)(buffer + SCRIPT_NAME_LEN_OFFSET));

        parsed_log->script_name = calloc(parsed_log->script_name_len + 1, 1);
        strncpy(parsed_log->script_name, buffer + SCRIPT_NAME_OFFSET, parsed_log->script_name_len);
        memset(parsed_log->script_name + parsed_log->script_name_len, 0x00, 1);

        parsed_log->next = &nullPLog;

        // Choose what to do based on the log's type
        // (should be 1 or 3 as we're having the socket throw out anything that isn't)
        // For type 1, set class_name_len and class_name to 0 and "N/A"
        switch (current_log.type)
        {
        case 1:
            parsed_log->class_name_len = 0;
            parsed_log->class_name = "N/A";
            parsed_log->function_name_len = *((long long *)(buffer + 56 + parsed_log->script_name_len));
            parsed_log->function_name = calloc(parsed_log->function_name_len + 1, 1);
            strncpy(parsed_log->function_name, buffer + 64 + parsed_log->script_name_len, parsed_log->function_name_len);
            memset(parsed_log->function_name + parsed_log->function_name_len, 0x00, 1);
            parsed_log->param_len = *((long long *)(buffer + 64 + parsed_log->script_name_len + parsed_log->function_name_len));
            parsed_log->param = buffer + 72 + parsed_log->script_name_len + parsed_log->function_name_len;
            break;
        case 3:
            parsed_log->class_name_len = *((long long *)(buffer + 56 + parsed_log->script_name_len));
            parsed_log->class_name = buffer + 64 + parsed_log->script_name_len;
            parsed_log->function_name_len = *((long long *)(buffer + 64 + parsed_log->script_name_len + parsed_log->class_name_len));
            parsed_log->function_name = calloc(parsed_log->function_name_len + 1, 1);
            strncpy(parsed_log->function_name, buffer + 72 + parsed_log->script_name_len + parsed_log->class_name_len, parsed_log->function_name_len);
            memset(parsed_log->function_name + parsed_log->function_name_len, 0x00, 1);
            parsed_log->param_len = *((long long *)(buffer + 72 + parsed_log->script_name_len + parsed_log->class_name_len + parsed_log->function_name_len));
            parsed_log->param = buffer + 80 + parsed_log->script_name_len + parsed_log->class_name_len + parsed_log->function_name_len;
            break;
        default:
            printf("LogTypeError: Log Parsing Thread Found Log of Wrong Type: %x\n", parsed_log->type);
            exit(EXIT_FAILURE);
            break;
        }

    #if WRITE_LOGS_TO_FILE
        write_parsed_log_to_file(logFile, *parsed_log); //TODO THIS WONT WORK CAUSE WE CHANGED TO POINTER WHO CARES
    #endif

        // Grab the p_queue mutex
        pthread_mutex_lock(&p_queue.mtx);
        // Add to parsed queue
        add_to_parsed_queue(parsed_log);
        // Release the p_queue mutex
        //pthread_mutex_unlock(&p_queue.mtx);  // PTHREAD_COND_TAG. This code was changed to avoid usleep(). It seems it didn't break anything

        // Cleanup
        fflush(stdout);
    }
    return 0;
}

// ----------------------------------------------------- MAIN SOCKET READING ----------------------------------------------------- //

//* Thread that will read log message header data from the socket,
//* then create an unparsed log with the header fields and body buffer
//* and add it to the unparsed_queue
extern void *read_from_socket(void *args)
{
    // Initialize the mtx
    pthread_mutex_init(&unp_queue.mtx, NULL);
    pthread_mutex_init(&p_queue.mtx, NULL);

    // Socket setup
    int server_file_descriptor, new_socket, value_read; // bunch of stuff to set up the socket
    struct sockaddr_in address;                         // struct to hold the address of the server
    int opt = 1;                                        // not really sure what this is for but apparently it's important and helps with binding errors
    int addrlen = sizeof(address);
    char len_buffer[9] = {0}; // buffer to hold the header of the message
    char buffer[BUFFER_SIZE] = {0};
    time_t timer;

    // Creating socket file descriptor
    if ((server_file_descriptor = socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Forcefully attaching socket to the port 10123
    if (setsockopt(server_file_descriptor, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)))
    {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;                // set the address family to IPv4
    address.sin_addr.s_addr = htonl(INADDR_ANY); // binds to all interfaces
    address.sin_port = htons(PORT);              // binds to port 10123

    // Forcefully attaching socket to the port 10123
    if (bind(server_file_descriptor, (struct sockaddr *)&address, sizeof(address)) < 0)
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_file_descriptor, 3) < 0)
    {
        perror("listen");
        exit(EXIT_FAILURE);
    }
    printf("Listening on port %d\n\n", PORT);

    // Start our read_logs_thread thread to parse from the unparsed_log queue
    pthread_t log_thread = 0;
    pthread_create(&log_thread, NULL, read_logs_thread, NULL);
    // }
    // Use a while loop to accept new clients, handing them off to handleClient threads
    //which accept their logs
    while((new_socket = accept(server_file_descriptor, (struct sockaddr *)&address, (socklen_t *)&addrlen))) {
        
        pthread_t handleClientThread = 0;
        pthread_create(&handleClientThread, NULL, handleClient, &new_socket); 

    }

    printf("Server log parsing exiting...\n");
    // Cleanup
    close(new_socket);
    shutdown(server_file_descriptor, SHUT_RDWR);

    return 0;
}

//* Thread function that is spin off for a new client and reads that client's unparsed logs
void *handleClient(void *socket) {

    char len_buffer[9] = {0}; // buffer to hold the header of the message
    char buffer[BUFFER_SIZE] = {0};

    int new_socket = *(int*)socket;
    
    for (;;) // listen forever
    {

        // Get the header of a message, along with it's type and msg_len
        int len_msg = read(new_socket, len_buffer, 9);
        char type = *len_buffer;
        long long msg_len = *((long long *)(len_buffer + 1));

        //  Exit if the log is malformed
        // This error is still unresolved. Future work could try to debug it
        // when looking into improving the log exfiltration method
        if ((type != 0x02 && type != 0x04 && type != 0x05 && type != 0x01 && type != 0x03) || msg_len > 1015)
        {
            printf("[SOCKET READ THREAD] Got malformed log. Type: %x Msg_len: %lld\n", type, msg_len);
            memset(buffer, 0, sizeof(buffer));
            continue;
        }

        // Get the entirety of the body
        int value_read = 0;
        while (value_read != msg_len)
        {
            value_read += read(new_socket, buffer + value_read, msg_len - value_read);
        }

        // Ignore messages that aren't types 0x01 or 0x03
        if (type == 0x02 || type == 0x04 || type == 0x05)
        {
            // Reset the buffer
            memset(buffer, 0, sizeof(buffer));
            continue;
        }

        // Create our unparsed_log struct
        struct unparsed_log unlog = {
            .type = type,
            .msg_len = msg_len,
            .msg_bodybuffer = {0},
            .next = &nullUnpLog};
        // Copy the buffer into our struct
        memcpy(unlog.msg_bodybuffer, buffer, sizeof(buffer));

        // Grab the unp_queue mutex
        pthread_mutex_lock(&unp_queue.mtx);
        // Add the log to the queue
        add_to_unparsed_queue(unlog);
        fflush(stdout);
        memset(buffer, 0, sizeof(buffer));
    }
}