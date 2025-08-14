#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <openssl/evp.h>
#include <openssl/crypto.h>
#include <string.h>
#include <omp.h>
#include <byteswap.h>
#define sm3_digest_BYTES 32
#define sm3_block_BYTES 64
#define sm3_hmac_BYTES sm3_digest_BYTES

typedef struct sm3_ctx_t_simd {
	uint32_t digest[sm3_digest_BYTES / sizeof(uint32_t)];
	int nblocks;
	uint8_t block[sm3_block_BYTES * 4];
	int num;
}sm3_ctx_simd;

void sm3_init_simd(sm3_ctx_simd* ctx);
void sm3_update_simd(sm3_ctx_simd* ctx, const uint8_t* data, size_t data_len);
void sm3_final_simd(sm3_ctx_simd* ctx, uint8_t* digest);

int sm3_hash_simd(uint8_t* dgst, const uint8_t* msg, size_t len);
int sm3_hash_verify_simd(const uint8_t* data, size_t dlen, const uint8_t* digest);

void sm3_init_simd(sm3_ctx_simd* ctx) {
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

#define P0(x) ((x) ^  rol((x),9)  ^ rol((x),17))
#define P1(x) ((x) ^  rol((x),15) ^ rol((x),23))

#define FF0(x,y,z) ( (x) ^ (y) ^ (z))
#define FF1(x,y,z) (((x) & (y)) | ( (x) & (z)) | ( (y) & (z)))

#define GG0(x,y,z) ( (x) ^ (y) ^ (z))
#define GG1(x,y,z) (((x) & (y)) | ( (~(x)) & (z)) )

__attribute__((target("default")))
void sm3_compress_simd(uint32_t digest[8], const unsigned char block[64])
{

	int j;
	uint32_t W[68], W1[64];
	const uint32_t* pblock = (const uint32_t*)block;

	uint32_t A = digest[0];
	uint32_t B = digest[1];
	uint32_t C = digest[2];
	uint32_t D = digest[3];
	uint32_t E = digest[4];
	uint32_t F = digest[5];
	uint32_t G = digest[6];
	uint32_t H = digest[7];
	uint32_t SS1, SS2, TT1, TT2;


	for (j = 0; j < 16; j++) W[j] = bswap_32(pblock[j]);

	for (j = 16; j < 68; j += 4) {
		W[j] = P1(W[j - 16] ^ W[j - 9] ^ rol(W[j - 3], 15)) ^ rol(W[j - 13], 7) ^ W[j - 6];
		W[j + 1] = P1(W[j + 1 - 16] ^ W[j + 1 - 9] ^ rol(W[j + 1 - 3], 15)) ^ rol(W[j + 1 - 13], 7) ^ W[j + 1 - 6];
		W[j + 2] = P1(W[j + 2 - 16] ^ W[j + 2 - 9] ^ rol(W[j + 2 - 3], 15)) ^ rol(W[j + 2 - 13], 7) ^ W[j + 2 - 6];
		W[j + 3] = P1(W[j + 3 - 16] ^ W[j + 3 - 9] ^ rol(W[j + 3 - 3], 15)) ^ rol(W[j + 3 - 13], 7) ^ W[j + 3 - 6];
	}
	/*W[64] = P1(W[48] ^ W[55] ^ rol(W[61], 15)) ^ rol(W[51], 7) ^ W[58];
	W[65] = P1(W[49] ^ W[56] ^ rol(W[62], 15)) ^ rol(W[52], 7) ^ W[59];
	W[66] = P1(W[50] ^ W[57] ^ rol(W[63], 15)) ^ rol(W[53], 7) ^ W[60];
	W[67] = P1(W[51] ^ W[58] ^ rol(W[64], 15)) ^ rol(W[54], 7) ^ W[61];*/

	for (j = 0; j < 64; j++) {
		W1[j] = W[j] ^ W[j + 4];
	}

	for (j = 0; j < 16; j += 2) {
		SS1 = rol((rol(A, 12) + E + rol(0x79CC4519, j)), 7);
		SS2 = SS1 ^ rol(A, 12);
		TT1 = FF0(A, B, C) + D + SS2 + W1[j];
		TT2 = GG0(E, F, G) + H + SS1 + W[j];
		D = C;
		C = rol(B, 9);
		B = A;
		A = TT1;
		H = G;
		G = rol(F, 19);
		F = E;
		E = P0(TT2);

		SS1 = rol((rol(A, 12) + E + rol(0x79CC4519, j + 1)), 7);
		SS2 = SS1 ^ rol(A, 12);
		TT1 = FF0(A, B, C) + D + SS2 + W1[j + 1];
		TT2 = GG0(E, F, G) + H + SS1 + W[j + 1];
		D = C;
		C = rol(B, 9);
		B = A;
		A = TT1;
		H = G;
		G = rol(F, 19);
		F = E;
		E = P0(TT2);
	}

	for (j = 16; j < 64; j += 2) {
		SS1 = rol((rol(A, 12) + E + rol(0x7A879D8A, j)), 7);
		SS2 = SS1 ^ rol(A, 12);
		TT1 = FF1(A, B, C) + D + SS2 + W1[j];
		TT2 = GG1(E, F, G) + H + SS1 + W[j];
		D = C;
		C = rol(B, 9);
		B = A;
		A = TT1;
		H = G;
		G = rol(F, 19);
		F = E;
		E = P0(TT2);

		SS1 = rol((rol(A, 12) + E + rol(0x7A879D8A, j + 1)), 7);
		SS2 = SS1 ^ rol(A, 12);
		TT1 = FF1(A, B, C) + D + SS2 + W1[j + 1];
		TT2 = GG1(E, F, G) + H + SS1 + W[j + 1];
		D = C;
		C = rol(B, 9);
		B = A;
		A = TT1;
		H = G;
		G = rol(F, 19);
		F = E;
		E = P0(TT2);
	}

	digest[0] ^= A;
	digest[1] ^= B;
	digest[2] ^= C;
	digest[3] ^= D;
	digest[4] ^= E;
	digest[5] ^= F;
	digest[6] ^= G;
	digest[7] ^= H;

}

__attribute__((target("default")))
void sm3_update_simd(sm3_ctx_simd* ctx, const uint8_t* data, size_t dlen) {
	if (ctx->num) {
		unsigned int left = sm3_block_BYTES - ctx->num;
		if (dlen < left) {
			memcpy(ctx->block + ctx->num, data, dlen);
			ctx->num += dlen;
			return;
		}
		else {
			memcpy(ctx->block + ctx->num, data, left);
			sm3_compress_simd(ctx->digest, ctx->block);
			ctx->nblocks++;
			data += left;
			dlen -= left;
		}
	}
	while (dlen >= sm3_block_BYTES) {
		sm3_compress_simd(ctx->digest, data);
		ctx->nblocks++;
		data += sm3_block_BYTES;
		dlen -= sm3_block_BYTES;
	}
	ctx->num = dlen;
	if (dlen) {
		memcpy(ctx->block, data, dlen);
	}
}

__attribute__((target("default")))
void sm3_final_simd(sm3_ctx_simd* ctx, uint8_t* digest) {
	size_t i;
	uint32_t* pdigest = (uint32_t*)(digest);
	uint64_t* count = (uint64_t*)(ctx->block + sm3_block_BYTES - 8);

	ctx->block[ctx->num] = 0x80;

	if (ctx->num + 9 <= sm3_block_BYTES) {
		memset(ctx->block + ctx->num + 1, 0, sm3_block_BYTES - ctx->num - 9);
	}
	else {
		memset(ctx->block + ctx->num + 1, 0, sm3_block_BYTES - ctx->num - 1);
		sm3_compress_simd(ctx->digest, ctx->block);
		memset(ctx->block, 0, sm3_block_BYTES - 8);
	}

	count[0] = (uint64_t)(ctx->nblocks) * 512 + (ctx->num << 3);
	count[0] = bswap_64(count[0]);

	sm3_compress_simd(ctx->digest, ctx->block);
	for (i = 0; i < sizeof(ctx->digest) / sizeof(ctx->digest[0]); i++) {
		pdigest[i] = bswap_32(ctx->digest[i]);
	}
}


int sm3_hash_simd(uint8_t* dgst, const uint8_t* msg, size_t len) {
	sm3_ctx_simd* md = new sm3_ctx_simd;

	sm3_init_simd(md);
	sm3_update_simd(md, msg, len);
	sm3_final_simd(md, dgst);
	return 0;
}

int sm3_hash_verify_simd(const uint8_t* msg, size_t len, const uint8_t* dgst) {
	uint8_t buf[32];
	sm3_hash_simd(buf, msg, len);
	return memcmp(buf, dgst, 32);
}