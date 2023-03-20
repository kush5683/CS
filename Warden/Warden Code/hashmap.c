// This is the best hashmap implementation.
#include "hashmap.h"
#include <string.h>

extern struct hashmap *pMap;

//* Malloc and initialize the hashmap
extern struct hashmap *hashmap_initialize()
{
    pMap = malloc(sizeof(struct hashmap));
    // Size of Hashmap must be prime and larger than the number of scripts
    pMap->size = 2939;
    pMap->buckets = (lookupScript **)malloc(pMap->size * sizeof(lookupScript *));
    if (pMap->buckets == NULL)
    {
        perror("malloc fail, big sad");
    }
    return pMap;
}

//* Free the hashmap
extern void hashmap_free(struct hashmap *map)
{
    if (!map)
        return;
    free(map);
}

//* Hash function got this from http://www.cse.yorku.ca/~oz/hash.html
extern unsigned long hash(unsigned char *str)
{
    unsigned long hash = 0;
    int c;

    while (c = *str++)
    {
        hash = c + (hash << 6) + (hash << 16) - hash;
    }

    // printf("hash: %lu\n", hash);

    return hash;
}

//* Set a lookupScript in the hashmap
extern int hashmap_set(struct hashmap *map, lookupScript *lookupScr)
{
    int idx = hash(lookupScr->name) % map->size;
    // add 7 to inx until no collision
    while (map->buckets[idx] != NULL)
    {
        idx = (idx + 7) % map->size;
    }
    map->buckets[idx] = lookupScr;
    return 0;
}

//* Retrieve a loopkupScript from the hashmap
extern lookupScript *hashmap_get(struct hashmap *map, char *fnName)
{
    int idx = hash(fnName) % map->size;
    // while name is not same add 7 to inx until no collision

    while (map->buckets[idx] != NULL && strcmp(map->buckets[idx]->name, fnName))
    {
        idx = (idx + 7) % map->size;
    }
    return map->buckets[idx];
}

//* Delete a lookupScript from the hashmap
extern lookupScript *hashmap_delete(struct hashmap *map, char *fnName)
{
    lookupScript *itemToDelete = hashmap_get(map, fnName);
    int idx = hash(fnName) % map->size;
    while (map->buckets[idx] != NULL && map->buckets[idx]->name != fnName)
    {
        idx = (idx + 7) % map->size;
    }
    map->buckets[idx] = NULL;
    return itemToDelete;
}

//* Helper to print the hashmap
extern void printMap(struct hashmap *map)
{
    printf("SIZE: %d\n", map->size);
    for (int i = 0; i < map->size; i++)
    {
        if (map->buckets[i] != NULL)
        {
            printf("Bucket %d: %s\n", i, map->buckets[i]->name);
            // Loop through callable functions and print them out if they exist
            callableFunction *current = map->buckets[i]->callableFunction;
            while (current != NULL)
            {
                printf("    %s:%d", current->name, current->lineno);
                current = current->next;
            }
            printf("\n\n");
        }
    }
}

//* Helper function that will be used for discovery analysis mode
//* Updates the hashmap to include the scriptname fnname relation given
//* Can either add a new scriptname with the fnname at the start of its list
//* OR adds the fnname to a scriptname's list if it is not already there
extern void addFromLogInfo(struct hashmap *map, char *scriptName, char *fnName, int lineno) {

    struct lookupScript *scriptEntry = hashmap_get(map, scriptName);

    // If the script is not in the hashmap, add it to the hashmap with the fnName as the
    // first function
    if(scriptEntry == NULL) {
        printf("[New Script]: %s: %s - %d\n", scriptName, fnName, lineno); //TODO remove later
        //Using the same method we use in manager.c:populateHashmap() to start a lookup function
        struct lookupScript *newScriptEntry = malloc(sizeof(struct lookupScript));

        struct callableFunction *firstFunction = malloc(sizeof(struct callableFunction));
        firstFunction->name = fnName;
        firstFunction->next = NULL;
        firstFunction->lineno = lineno;

        newScriptEntry->name = scriptName;
        newScriptEntry->callableFunction = firstFunction;
        hashmap_set(map, newScriptEntry);
    } 
    else {
        // Add the fnName to the end of the callableFn list IF it is not already there
        callableFunction *current = scriptEntry->callableFunction;
        // Get the end of the list
        while (current->next != NULL)
        {
            // If the function is already here break
            if(!strncmp(current->name, fnName, strlen(fnName)) && current->lineno == lineno) {
                return;
            }
            current = current->next;
        }

        // If the function is already here break
        if(!strncmp(current->name, fnName, strlen(fnName)) && current->lineno == lineno) {
            return;
        }
        printf("[New Function]: %s: %s - %d\n", scriptName, fnName, lineno); //TODO remove later
        // Now current is the last thing in the list
        struct callableFunction *newFunction = malloc(sizeof(struct callableFunction));\
        newFunction->name = fnName;
        newFunction->next = NULL;
        newFunction->lineno = lineno;
        // Add it to the end of the list
        current->next = newFunction;
    }

}

//* Write the contents of the Hashmap to a file for persistent storage
//* Use same format as used in static_analysis.py
extern void writeHashmapToFile(struct hashmap *map, FILE* fp) {

    // For each script
    for(int index = 0; index < map->size; index++) {

        // Only print the buckets that are not null
        if(map->buckets[index] == NULL) {
            continue;
        }

        // Print "script_name: "
        fprintf(fp, "%s: ", map->buckets[index]->name);

        // Print each callableFunction with a space after it
        callableFunction *current = map->buckets[index]->callableFunction;
        while (current != NULL)
        {
            if(!strncmp(current->name, "\n", 1)) { break; } // hacky fix to not print when the last callableFunction is a "\n"
            fprintf(fp, "%s|%d ", current->name, current->lineno);
            current = current->next;
        }
        fprintf(fp, "\n");

    }

    return;
}

extern int test()
{

    struct callableFunction s1oneCF = {.name = "ONE", .next = NULL};
    struct callableFunction s2oneCF = {.name = "S2ONE", .next = NULL};
    struct callableFunction s2twoCF = {.name = "S2TWO", .next = &s2oneCF};
    struct callableFunction s5oneCF = {.name = "KETIH", .next = NULL};

    // hashmap_set(testMap, &(struct lookupScript){.name = "SCRIPT_1", .callableFunction = &s1oneCF});
    // hashmap_set(testMap, &(struct lookupScript){.name = "SCRIPT_2", .callableFunction = &s2twoCF});
    // addFromLogInfo(testMap, "SCRIPT_3", "S2TWO");
    // addFromLogInfo(testMap, "SCRIPT_3", "ONE");
    // addFromLogInfo(testMap, "SCRIPT_1", "tee");
    // addFromLogInfo(testMap, "SCRIPT_2", "S2ONE");
    // addFromLogInfo(testMap, "SCRIPT_2", "gee");
    // addFromLogInfo(testMap, "SCRIPT_2", "gee");
    // addFromLogInfo(testMap, "SCRIPT_2", "S2TWO");
    // hashmap_set(testMap, &(struct lookupScript){.name = "SCRIPT_4", .callableFunction = NULL});
    // hashmap_set(testMap, &(struct lookupScript){.name = "SCRIPT_5", .callableFunction = &s5oneCF});

    // FILE *fp;
    // fp = fopen("keithWritingTest.txt", "w");
    // writeHashmapToFile(testMap, fp);
    // printMap(testMap);
}