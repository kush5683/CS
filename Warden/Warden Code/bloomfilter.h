#ifndef BLOOM_H
#define BLOOM_H

#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <time.h>
#include <pthread.h>
#include <execinfo.h>
#include <execinfo.h>
#include <signal.h>

//* Struct used as the bit array. Done by making a "list" of bytes, using 1 byte long uint8_t data type
typedef struct bit_array
{
    uint8_t *bits;
    size_t number_bits;
} bit_array;
// This can be thought of as being "chunks" of 8, so you can find out how many chunks in your index is, then how many bits into the 8 bit chunk it is

//* This defines a kind of function that will fit into our goal of "hash" function. Will return a hash
//* that we can mold to the size we need with %. This will then be used as a bit_index
//* to set to 1 in the bloom filter bit_array.
typedef uint32_t (*hash_function)(char *entry, size_t length_of_entry);

//* This is our bloom filter struct
struct bloom_filter
{
    bit_array *bit_array;
    hash_function *hash_functions;
    size_t num_functions;
    size_t num_entries;
};

// Hash functions
uint32_t sdbm(char *entry, size_t length_of_entry);
uint32_t djb2(char *entry, size_t length_of_entry);
uint32_t murmur3_32(char *entry, size_t length_of_entry);

bit_array *new_bit_array(size_t number_bits);
extern struct bloom_filter *init_bloom_filter(size_t number_functions, size_t number_bits, hash_function *hash_functions);
int set_bit(struct bloom_filter *filter, size_t bit_offset, int value);
int get_bit(struct bloom_filter *filter, size_t bit_offset);
extern void put_bloom_filter(struct bloom_filter *bloom_filter, char *entry);
extern int check_if_in_bloom_filter(struct bloom_filter *bloom_filter, char *entry);
void free_bloom_filter(struct bloom_filter *filter);
extern void print_bloom_filter(struct bloom_filter *filter);
extern struct bloom_filter *bloomfilter_initialize();

#endif