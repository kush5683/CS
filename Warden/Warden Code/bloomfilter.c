#include "bloomfilter.h"
#include <math.h>

#define BITS_PER_BYTE 8
#define BITS_IN_TYPE(type) (BITS_PER_BYTE * (sizeof(type)))
#define CHUNK_TYPE uint8_t
#define CHUNK_SIZE BITS_IN_TYPE(CHUNK_TYPE)
// Size of the bloom filter in bits
#define FILTER_SIZE 80000000
#define NUM_HASH_FUNC 5

/* Bloom Filter API, based on https://www.andreinc.net/2022/03/01/on-implementing-bloom-filters-in-c */

// ------------------------------------ STRUCTS AND DEFINED CONSTANTS ------------------------------------ //
extern struct bloom_filter *bf;
hash_function *h_functions;
// ------------------------------------ HASH FUNCTIONS ------------------------------------ //

//* https://api.riot-os.org/group__sys__hashes__sdbm.html#:~:text=sdbm%20hash%20algorithm.-,sdbm%20hash%20algorithm.,hashing%20function%20with%20good%20distribution.
uint32_t
sdbm(char *entry, size_t length_of_entry)
{
    uint32_t hash_value = 0;
    for (size_t i = 0; i < length_of_entry; i++)
    {
        hash_value = (hash_value << 6) + (hash_value << 16) + entry[i] - hash_value;
    }
    return hash_value;
}

//* http://www.cse.yorku.ca/~oz/hash.html
uint32_t djb2(char *entry, size_t length_of_entry)
{
    uint32_t hash_value = 5381;
    for (size_t i = 0; i < length_of_entry; i++)
    {
        hash_value = ((hash_value << 5) + hash_value) + entry[i];
    }
    return hash_value;
}

//* https://en.wikipedia.org/wiki/MurmurHash
uint32_t murmur3_32(char *entry, size_t length_of_entry)
{
    uint32_t h = 1133045564;
    uint32_t k;
    /* Read in groups of 4. */
    for (size_t i = length_of_entry >> 2; i; i--)
    {
        // Here is a source of differing results across endiannesses.
        // A swap here has no effects on hash properties though.
        memcpy(&k, entry, sizeof(uint32_t));
        entry += sizeof(uint32_t);
        k *= 0xcc9e2d51;
        k = (k << 15) | (k >> 17);
        k *= 0x1b873593;
        h ^= k;
        h = (h << 13) | (h >> 19);
        h = h * 5 + 0xe6546b64;
    }
    /* Read the rest. */
    k = 0;
    for (size_t i = length_of_entry & 3; i; i--)
    {
        k <<= 8;
        k |= entry[i - 1];
    }
    // A swap is *not* necessary here because the preceding loop already
    // places the low bytes in the low places according to whatever endianness
    // we use. Swaps only apply when the memory is copied in a chunk.
    k *= 0xcc9e2d51;
    k = (k << 15) | (k >> 17);
    k *= 0x1b873593;
    h ^= k;
    /* Finalize. */
    h ^= length_of_entry;
    h ^= h >> 16;
    h *= 0x85ebca6b;
    h ^= h >> 13;
    h *= 0xc2b2ae35;
    h ^= h >> 16;
    return h;
}

//* https://www.digitalocean.com/community/tutorials/hash-table-in-c-plus-plus
uint32_t fullStringHash(char *entry, size_t length_of_entry) {
    uint32_t h = 0;
    for(int i = 0; i < length_of_entry; i++) {
        h += entry[i];
    }
    return h % FILTER_SIZE;
}

//* https://www.geeksforgeeks.org/hash-functions-and-list-types-of-hash-functions/
uint32_t multiplicationHash(char *entry, size_t length_of_entry) {
    uint32_t h = 0;
    for(int i = 0; i < length_of_entry; i++) {
        h += entry[i];
    }
    return (uint32_t) floor(FILTER_SIZE * (0.357840*h - floor(0.357840*h)));
}

// ------------------------------------ BLOOM FILTER API FUNCTIONS ------------------------------------ //

//* Makes a new bit_array
bit_array *new_bit_array(size_t number_bits)
{
    // Allocate the bit_array itself
    bit_array *bit_array = malloc(sizeof(*bit_array));
    if (NULL == bit_array)
    {
        printf("Out of heap memory when allocating bit_array.\n");
        exit(EXIT_FAILURE);
    }
    // Get the number of chunks that we will use
    size_t number_chunks = number_bits / CHUNK_SIZE;
    // Check if number_bits is not a multiple of CHUNK_SIZE, and add the appropriate extra CHUNCK
    if (!(number_bits % CHUNK_SIZE))
    {
        number_chunks++;
    }
    // calloc() takes the number of elements and size of an element and allocates that much space then sets it to 0
    bit_array->bits = calloc(number_chunks, sizeof(*(bit_array->bits)));
    if (bit_array->bits == NULL)
    {
        printf("Out of heap memory when allocating bit_array->bits.\n");
        exit(EXIT_FAILURE);
    }
    bit_array->number_bits = number_bits;
    return bit_array;
}

//* Creating a new bloom filter
extern struct bloom_filter *init_bloom_filter(size_t number_functions, size_t number_bits, hash_function *hash_functions)
{

    h_functions = malloc(sizeof(hash_function) * number_functions);

    if (h_functions == NULL)
    {
        printf("Error: No heap space when mallocing hash functions.\n");
        exit(EXIT_FAILURE);
    }
    h_functions[0] = sdbm;
    h_functions[1] = djb2;
    h_functions[2] = murmur3_32;
    h_functions[3] = fullStringHash;
    h_functions[4] = multiplicationHash;

    // Allocate the filter
    bf = malloc(sizeof(struct bloom_filter));
    if (NULL == bf)
    {
        printf("Out of heap memory when allocating bloom_filter.\n");
        exit(EXIT_FAILURE);
    }

    // Set starting values
    bf->hash_functions = h_functions;
    bf->num_entries = 0;
    bf->num_functions = number_functions;
    bf->bit_array = new_bit_array(number_bits);

    return bf;
}

//* Sets the bit at bit_offset of bloom_filter's bit_array to value.
int set_bit(struct bloom_filter *filter, size_t bit_offset, int value)
{

    bit_array *bit_array = filter->bit_array;

    if (value != 1 && value != 0)
    {
        printf("Error Invalid Value Passed to set_bit_array()\n");
        exit(EXIT_FAILURE);
    }
    if (bit_offset > bit_array->number_bits || bit_offset < 0)
    {
        printf("Error: Bit Offset passed to set_bit_array() out of bounds. Offset: %ld Bounds: %ld\n", bit_offset, bit_array->number_bits);
        exit(EXIT_FAILURE);
    }

    size_t chunk_offset = bit_offset / CHUNK_SIZE;
    size_t bit_index = bit_offset % CHUNK_SIZE;

    uint8_t *chunk = &(bit_array->bits[chunk_offset]);

    if (value == 1)
    {
        // Sets the bit of chunk at bit_index to 1
        *chunk |= 1UL << bit_index;
    }
    else
    {
        // Sets the bit of chunk at bit_index to 0
        *chunk &= ~(1UL << bit_index);
    }

    return 0;
}

//* Gets the bit value at a bit_offset.
int get_bit(struct bloom_filter *filter, size_t bit_offset)
{
    bit_array *bit_array = filter->bit_array;
    if (bit_offset > bit_array->number_bits || bit_offset < 0)
    {
        printf("Error: Bit Offset passed to get_bit_array() out of bounds. Offset: %ld Bounds: %ld\n", bit_offset, bit_array->number_bits);
        exit(EXIT_FAILURE);
    }

    size_t chunk_offset = bit_offset / CHUNK_SIZE;
    size_t bit_index = bit_offset % CHUNK_SIZE;
    uint8_t chunk = bit_array->bits[chunk_offset];

    return (chunk >> bit_index) & 1;
}

//* Putting an entry into the bloom filter (assuming we're saving entries as strings encoded a certain way)
extern void put_bloom_filter(struct bloom_filter *bloom_filter, char *entry)
{

    for (int h_func = 0; h_func < bloom_filter->num_functions; h_func++)
    {
        // Hash and modulos it into our bit array size
        size_t bit_offset = bloom_filter->hash_functions[h_func](entry, strlen(entry)) % bloom_filter->bit_array->number_bits;
        set_bit(bloom_filter, bit_offset, 1);
    }
    bloom_filter->num_entries++;
}

//* Check if a entry is in the bloom filter
extern int check_if_in_bloom_filter(struct bloom_filter *bloom_filter, char *entry)
{
    for (int h_func = 0; h_func < bloom_filter->num_functions; h_func++)
    {
        size_t bit_offset = bloom_filter->hash_functions[h_func](entry, strlen(entry)) % bloom_filter->bit_array->number_bits;
        if (!get_bit(bloom_filter, bit_offset))
        {
            // Then it is not in the filter
            return 0;
        }
    }
    return 1;
}

//* Function to free bloom filter and all of it's attributes that have been allocated
void free_bloom_filter(struct bloom_filter *filter)
{
    free(filter->bit_array->bits);
    free(filter->bit_array);
    free(filter->hash_functions);
    free(filter);
}

//* Prints the bit array in a humanreable format
extern void print_bloom_filter(struct bloom_filter *filter)
{

    bit_array *bit_array = filter->bit_array;

    printf("------------------- BLOOM FILTER -------------------\n");
    printf("Filter size: %ld\n", bit_array->number_bits);
    printf("Number Of Hash Functions: %ld\n", filter->num_functions);
    printf("Number Of Entries: %ld\n", filter->num_entries);
    printf("------------------- Bit Array -------------------\n");
    printf("CHUNK SIZE: %ld\n", CHUNK_SIZE);
    for (int chunk = 0; chunk < bit_array->number_bits / CHUNK_SIZE; chunk++)
    {
        for (int bit = 0; bit < CHUNK_SIZE; bit++)
        {
            if ((bit_array->bits[chunk] >> bit) & 1)
            {
                printf("1\t");
            }
            else
            {
                printf("0\t");
            }
        }
        printf("\n");
    }
    printf("----------------------------------------------------\n");
}

//* External function called by manager to initialize bloomfilter
extern struct bloom_filter *bloomfilter_initialize()
{
    init_bloom_filter(NUM_HASH_FUNC, FILTER_SIZE, h_functions);
    return bf;
}
