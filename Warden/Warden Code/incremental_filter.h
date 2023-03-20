#ifndef INCREMENTAL_H
#define INCREMENTAL_H

#include "CFI_CONFIG.h"

// Function struct for the FBAD table
typedef struct functionEntry
{
    char *entry;
    int num_occurences;
    struct functionEntry *next;
    int lineno;
} functionEntry;

// Script struct that has a linked list of all functions it can call
typedef struct scriptKey
{
    char *scriptName;
    struct functionEntry *functionEntry;
} scriptKey;

// FBAD table struct
struct lookupTable
{
    int size;
    scriptKey **buckets;
};


extern struct lookupTable *lookupTable_initialize();
extern int lookupTable_query(struct lookupTable *map, char *scriptName, char *entry, int lineno);
extern void printLookupTable(struct lookupTable *map);
extern void writeOutLookupTable(struct lookupTable *map);
extern void incrementFunctionCall(struct lookupTable *map, char *scriptName, char *fnName, int lineno);
extern void lookupTable_free(struct lookupTable *map);
extern int lookupTable_set(struct lookupTable *map, scriptKey *scriptKey);
extern scriptKey *lookupTable_get(struct lookupTable *map, char *scriptName);

#endif