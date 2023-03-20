#ifndef HASHMAP_H
#define HASHMAP_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// This contains a name of a function that can be called by the lookupScript that contains it and a pointer to the next callableFunction
typedef struct callableFunction
{
    char *name;
    struct callableFunction *next;
    int lineno;
} callableFunction;

// This is the function name that we are transferring from, and we want to know what it is allowed to call
typedef struct lookupScript
{
    char *name;
    struct callableFunction *callableFunction;
} lookupScript;

struct hashmap
{
    int size;
    lookupScript **buckets;
};

extern struct hashmap *hashmap_initialize();
extern unsigned long hash(unsigned char *str);
extern void hashmap_free(struct hashmap *map);
extern int hashmap_set(struct hashmap *map, lookupScript *lookupScr);
extern lookupScript *hashmap_get(struct hashmap *map, char *fnName);
extern lookupScript *hashmap_delete(struct hashmap *map, char *fnName);
extern void printMap(struct hashmap *map);
extern void addFromLogInfo(struct hashmap *map, char *scriptName, char *fnName, int lineno);
extern void writeHashmapToFile(struct hashmap *map, FILE* fp);

#endif
