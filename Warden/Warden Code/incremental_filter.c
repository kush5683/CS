#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "incremental_filter.h"

// Alternative Lightweight CFI method that wasn't used due to a memory leak that we didn't have time to debug
// Called: Frequency Based Anomaly Detection (FBAD), Incremental Filter, and Lookup Table

// FBAD table external variable
extern struct lookupTable *lupt;

// Used for debugging
int maxNum = 0;

//* Malloc and initialize the FBAD table
extern struct lookupTable *lookupTable_initialize()
{
    lupt = malloc(sizeof(struct lookupTable));
    // Size of hashmap, must be prime and larger than the total number of scripts
    lupt->size = 2939;
    lupt->buckets = (scriptKey **)malloc(lupt->size * sizeof(scriptKey *));
    if (lupt->buckets == NULL)
    {
        printf("malloc fail, big sad");
        exit(EXIT_FAILURE);
    }
    return lupt;
}

//* Function to free the FBAD table
extern void lookupTable_free(struct lookupTable *map)
{
    if (!map)
        return;
    free(map);
}

//* Hash function, got this from http://www.cse.yorku.ca/~oz/hash.html
unsigned long hash_lookupTable(unsigned char *str)
{
    unsigned long hash = 0;
    int c;

    while (c = *str++)
    {
        hash = c + (hash << 6) + (hash << 16) - hash;
    }

    return hash;
}

//* Set a scriptKey in the table
extern int lookupTable_set(struct lookupTable *map, scriptKey *scriptKey)
{
    int idx = hash_lookupTable(scriptKey->scriptName) % map->size;
    // add 7 to inx until no collision
    while (map->buckets[idx] != NULL)
    {
        idx = (idx + 7) % map->size;
    }
    map->buckets[idx] = scriptKey;
    return 0;
}

//* Retrieve a scriptKey from the table
extern scriptKey *lookupTable_get(struct lookupTable *map, char *scriptName)
{
    int idx = hash_lookupTable(scriptName) % map->size;
    // while name is not same add 7 to inx until no collision

    while (map->buckets[idx] != NULL && strcmp(map->buckets[idx]->scriptName, scriptName))
    {
        idx = (idx + 7) % map->size;
    }
    return map->buckets[idx];
}

//* Delete a scriptKey from the table
extern scriptKey *lookupTable_delete(struct lookupTable *map, char *fnName)
{
    scriptKey *itemToDelete = lookupTable_get(map, fnName);
    int idx = hash_lookupTable(fnName) % map->size;
    while (map->buckets[idx] != NULL && map->buckets[idx]->scriptName != fnName)
    {
        idx = (idx + 7) % map->size;
    }
    map->buckets[idx] = NULL;
    return itemToDelete;
}

//* Used for debugging, get the maximum number of occurences in the lookup table
void maxNumber(struct lookupTable *map) {
    for(int i = 0; i < map->size; i++) {
        if(map->buckets[i] != NULL) {
            struct functionEntry *current = map->buckets[i]->functionEntry;
            while(current != NULL) {
                if(current->num_occurences > maxNum) {
                    printf("New max found: %d Function: %s, Script: %s\n\n", current->num_occurences, current->entry, map->buckets[i]->scriptName);
                    maxNum = current->num_occurences;
                }
                current = current->next;
            }

        }
    }
}

//* Query the FBAD table to determine if a function call is trusted or not
//* Returns True if the given function call has been seen >= NUM_TRUSTED_OCCURENCES,
//* False otherwise
extern int lookupTable_query(struct lookupTable *map, char *scriptName, char *entry, int lineno) {
    
    struct scriptKey *sk = lookupTable_get(map, scriptName);

    // Script is not in lookup table
    if(sk == NULL) {
        return 0;
    }

    struct functionEntry *current = sk->functionEntry;

    // Iterate through each of the script's valid functions
    while(current != NULL) {

        // If the function exists, return True if it has been seen a trusted number of times
        if(!strcmp(current->entry, entry) && lineno == current->lineno) {
            return current->num_occurences >= NUM_TRUSTED_OCCURENCES;
        }

        current = current->next;

    }
    // Function is not in lookup table
    return 0;
}

//* Prints out lookup table
extern void printLookupTable(struct lookupTable *map)
{
    printf("SIZE: %d\n", map->size);
    for (int i = 0; i < map->size; i++)
    {
        if (map->buckets[i] != NULL)
        {
            printf("Bucket %d: %s\n", i, map->buckets[i]->scriptName);
            // Loop through callable functions and print them out if they exist
            functionEntry *current = map->buckets[i]->functionEntry;
            while (current != NULL)
            {
                printf("    %s:%d - %d", current->entry, current->lineno, current->num_occurences);
                current = current->next;
            }
            printf("\n\n");
        }
    }
}

//* Writes lookup table to file
extern void writeOutLookupTable(struct lookupTable *map) {
    FILE *fp = fopen("incremental_filter_printout.txt", "w");
    fprintf(fp, "SIZE: %d\n", map->size);
    for (int i = 0; i < map->size; i++)
    {
        if (map->buckets[i] != NULL)
        {
            fprintf(fp, "Bucket %d: %s\n", i, map->buckets[i]->scriptName);
            // Loop through callable functions and print them out if they exist
            functionEntry *current = map->buckets[i]->functionEntry;
            while (current != NULL)
            {
                fprintf(fp, "    %s:%d - %d", current->entry, current->lineno, current->num_occurences);
                current = current->next;
            }
            fprintf(fp, "\n\n");
        }
    }
    fclose(fp);
}

//* Increments the number of times we've seen a given function call. 
//* Handles adding it to the lookupTable if it's not there
extern void incrementFunctionCall(struct lookupTable *map, char *scriptName, char *entry, int lineno) {

    struct scriptKey *scriptEntry = lookupTable_get(map, scriptName);

    // If the script is not in the lookupTable, add it to the lookupTable with the fnName as the
    // first function
    if(scriptEntry == NULL) {
    #if DEBUG
        printf("Adding new script: %s with function: %s to lookup table\n", scriptName, entry);
    #endif

        struct scriptKey *newScriptEntry = malloc(sizeof(struct scriptKey));

        struct functionEntry *firstFunction = malloc(sizeof(struct functionEntry));
        firstFunction->entry = entry;
        firstFunction->num_occurences = 1;
        firstFunction->next = NULL;
        firstFunction->lineno = lineno;

        newScriptEntry->scriptName = scriptName;
        newScriptEntry->functionEntry = firstFunction;
        lookupTable_set(map, newScriptEntry);
    } 
    else {
        // Add the fnName to the end of the callableFn list IF it is not already there
        functionEntry *current = scriptEntry->functionEntry;
        // Get the end of the list
        while (current->next != NULL)
        {
            // If the function is already here increment
            if(!strcmp(current->entry, entry) && lineno == current->lineno) {
                current->num_occurences += 1;
                return;
            }
            current = current->next;
        }

        // If the function is already here incremenet
        if(!strcmp(current->entry, entry) && lineno == current->lineno) {
            current->num_occurences += 1;
            return;
        }
    #if DEBUG
        printf("Adding new function: %s to the script: %s in lookup table\n", entry, scriptName);
    #endif
        // Now current is the last thing in the list
        struct functionEntry *newFunction = malloc(sizeof(struct functionEntry));
        newFunction->entry = entry;
        newFunction->num_occurences = 1;
        newFunction->next = NULL;
        newFunction->lineno = lineno;
        // Add it to the end of the list
        current->next = newFunction;
    }

}

// For testing
int testFunc() {

    struct lookupTable *lut = lookupTable_initialize();

    // struct functionEntry entry1 = { .entry="testfunc:14", .next=NULL };
    // struct functionEntry entry2 = { .entry="sam:69", .next=&entry1 };
    // struct scriptKey script1 = { .scriptName = "keith.php", .functionEntry=&entry2 };

    incrementFunctionCall(lut, "k.php", "samFUNCTION", 741);
    incrementFunctionCall(lut, "k.php", "samFUNCTION", 741);
    incrementFunctionCall(lut, "k.php", "samFUNCTION", 741);
    incrementFunctionCall(lut, "k.php", "samFUNCTION", 741);
    incrementFunctionCall(lut, "k.php", "samFUNCTION", 742);
    incrementFunctionCall(lut, "k.php", "samFUNCTION", 742);
    incrementFunctionCall(lut, "k.php", "KSUHATACK", 87);
    incrementFunctionCall(lut, "f.php", "KSUHATACK", 87);
    incrementFunctionCall(lut, "f.php", "KSUHATACK", 87);
    incrementFunctionCall(lut, "f.php", "KSUHATACK", 87);
    incrementFunctionCall(lut, "f.php", "KSUHATACK", 87);
    incrementFunctionCall(lut, "f.php", "KSUHATACK", 87);
    incrementFunctionCall(lut, "f.php", "KSUHATACK", 87);
    
    
    printLookupTable(lut);
    printf("\n\n");

    return 0;
}