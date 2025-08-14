#pragma once
#include <stdint.h>
#include <immintrin.h>
#include <stdlib.h>
#include <stdio.h>
#include <openssl/evp.h>
#include <openssl/crypto.h>
#include<string.h>
#include <byteswap.h>
#define sm3_digest_BYTES 32
#define sm3_block_BYTES 64
#define sm3_hmac_BYTES sm3_digest_BYTES

typedef struct sm3_ctx_t {
	uint32_t digest[sm3_digest_BYTES / sizeof(uint32_t)];
	int nblocks;
	uint8_t block[sm3_block_BYTES * 4];
	int num;
}sm3_ctx;

void sm3_init(sm3_ctx* ctx);
void sm3_update(sm3_ctx* ctx, const uint8_t* data, size_t data_len, uint8_t* copy, int& times);
void sm3_final(sm3_ctx* ctx, uint8_t* digest, uint8_t* copy, int& times);

void sm3_init(sm3_ctx* ctx) {
	ctx->digest[0] = 0x7380166F;
	ctx->digest[1] = 0x49148289;
	ctx->digest[2] = 0x172442D7;
	ctx->digest[3] = 0xDA8A0600;
	ctx->digest[4] = 0xA96F30BC;
	ctx->digest[5] = 0x163138AA;
	ctx->digest[6] = 0xE38DEE4D;
	ctx->digest[7] = 0xB0FB0E4E;

	ctx->nblocks = 0;
	ctx->num = 0;
}

#define rol(X,n)  (((X)<<(n)) | ((X)>>(32-(n))))

#define P00(x) (_mm_xor_si128(_mm_xor_si128(_mm_xor_si128(x, _mm_slli_epi32(x, 9)), _mm_slli_epi32(x, 17)), _mm_srli_epi32(x, 25)))
#define P01(x) (_mm_xor_si128(_mm_xor_si128(_mm_xor_si128(x, _mm_slli_epi32(x, 15)), _mm_slli_epi32(x, 23)), _mm_srli_epi32(x, 7)))

#define P0(x) ((x) ^  rol((x),9)  ^ rol((x),17))
#define P1(x) ((x) ^  rol((x),15) ^ rol((x),23))

#define FF0(x,y,z) ( (x) ^ (y) ^ (z))
#define FF1(x,y,z) (((x) & (y)) | ( (x) & (z)) | ( (y) & (z)))

#define GG0(x,y,z) ( (x) ^ (y) ^ (z))
#define GG1(x,y,z) (((x) & (y)) | ( (~(x)) & (z)) )

static void sm3_compress(uint32_t digest[sm3_digest_BYTES / sizeof(uint32_t)], const uint8_t block[sm3_block_BYTES]) {
	int j;
	uint32_t W[68], W1[64];
	const uint32_t* pblock = (const uint32_t*)(block);

	uint32_t A = digest[0], B = digest[1], C = digest[2], D = digest[3];
	uint32_t E = digest[4], F = digest[5], G = digest[6], H = digest[7];

	uint32_t SS1, SS2, TT1, TT2, T[64];

	for (j = 0; j < 16; j++) W[j] = bswap_32(pblock[j]);

	for (j = 16; j < 68; j++) {
		W[j] = P1(W[j - 16] ^ W[j - 9] ^ rol(W[j - 3], 15)) ^ rol(W[j - 13], 7) ^ W[j - 6];
	}

	for (j = 0; j < 64; j++)W1[j] = W[j] ^ W[j + 4];

	for (j = 0; j < 16; j++) {
		T[j] = 0x79CC4519;
		SS1 = rol((rol(A, 12) + E + rol(T[j], j)), 7);
		SS2 = SS1 ^ rol(A, 12);
		TT1 = FF0(A, B, C) + D + SS2 + W1[j];
		TT2 = GG0(E, F, G) + H + SS1 + W[j];
		D = C, C = rol(B, 9), B = A, A = TT1;
		H = G, G = rol(F, 19), F = E, E = P0(TT2);
	}

	for (j = 16; j < 64; j++) {
		T[j] = 0x7A879D8A;
		SS1 = rol((rol(A, 12) + E + rol(T[j], j)), 7);
		SS2 = SS1 ^ rol(A, 12);
		TT1 = FF1(A, B, C) + D + SS2 + W1[j];
		TT2 = GG1(E, F, G) + H + SS1 + W[j];
		D = C, C = rol(B, 9), B = A, A = TT1;
		H = G, G = rol(F, 19), F = E, E = P0(TT2);
	}

	digest[0] ^= A, digest[1] ^= B, digest[2] ^= C, digest[3] ^= D;
	digest[4] ^= E, digest[5] ^= F, digest[6] ^= G, digest[7] ^= H;
}


void sm3_update(sm3_ctx* ctx, const uint8_t* data, size_t dlen, uint8_t* copy, int& times) {
	if (ctx->num) {
		unsigned int left = sm3_block_BYTES - ctx->num;
		if (dlen < left) {
			memcpy(ctx->block + ctx->num, data, dlen);
			ctx->num += dlen;
			return;
		}
		else {
			
			memcpy(ctx->block + ctx->num, data, left);
			memcpy(copy + 64 * times, ctx->block, 64);
			sm3_compress(ctx->digest, ctx->block);
			times++;
			ctx->nblocks++;
			data += left;
			dlen -= left;
		}
	}
	while (dlen >= sm3_block_BYTES) {
		memcpy(copy + 64 * times, data, 64);
		sm3_compress(ctx->digest, data);
		times++;
		ctx->nblocks++;
		data += sm3_block_BYTES;
		dlen -= sm3_block_BYTES;
	}
	ctx->num = dlen;
	if (dlen) {
		memcpy(ctx->block, data, dlen);
	}
}

void sm3_final(sm3_ctx* ctx, uint8_t* digest, uint8_t* copy, int& times) {
	size_t i;
	uint32_t* pdigest = (uint32_t*)(digest);
	uint64_t* count = (uint64_t*)(ctx->block + sm3_block_BYTES - 8);

	ctx->block[ctx->num] = 0x80;

	if (ctx->num + 9 <= sm3_block_BYTES) {
		memset(ctx->block + ctx->num + 1, 0, sm3_block_BYTES - ctx->num - 9);
	}
	else {
		memset(ctx->block + ctx->num + 1, 0, sm3_block_BYTES - ctx->num - 1);
		memcpy(copy + 64 * times, ctx->block, 64);
		sm3_compress(ctx->digest, ctx->block);
		times++;
		memset(ctx->block, 0, sm3_block_BYTES - 8);
	}

	count[0] = (uint64_t)(ctx->nblocks) * 512 + (ctx->num << 3);
	count[0] = bswap_64(count[0]);

	memcpy(copy + 64 * times, ctx->block, 64);
	sm3_compress(ctx->digest, ctx->block);
	times++;
	for (i = 0; i < sizeof(ctx->digest) / sizeof(ctx->digest[0]); i++) {
		pdigest[i] = bswap_32(ctx->digest[i]);
	}
}