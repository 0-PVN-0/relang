/*
 * Monocypher CLI — stdin/stdout hex protocol for test harnesses.
 *
 * Reads  function_name \n param_hex : \n param_hex : \n ...  from stdin,
 * writes result_hex : \n result_hex : \n ...                     to stdout.
 *
 * Build:  make monocypher-cli
 *   or:   gcc -std=c99 -O3 -o monocypher-cli src/monocypher-cli.c \
 *             src/monocypher.c src/optional/monocypher-ed25519.c \
 *             -Isrc -Isrc/optional
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

#include "monocypher.h"
#include "optional/monocypher-ed25519.h"

#define MAX_LINE 1048576
#define MAX_PARAMS 64

static int hex_val(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static size_t hex_decode(uint8_t *out, size_t out_size, const char *hex) {
    size_t len = strlen(hex);
    if (len % 2 != 0) { fprintf(stderr, "odd hex len: %s\n", hex); exit(1); }
    size_t olen = len / 2;
    if (olen > out_size) { fprintf(stderr, "hex too long\n"); exit(1); }
    for (size_t i = 0; i < olen; i++) {
        int hi = hex_val(hex[2*i]);
        int lo = hex_val(hex[2*i + 1]);
        if (hi < 0 || lo < 0) { fprintf(stderr, "bad hex: %s\n", hex); exit(1); }
        out[i] = (uint8_t)((hi << 4) | lo);
    }
    return olen;
}

static void print_hex(const uint8_t *buf, size_t size) {
    for (size_t i = 0; i < size; i++) printf("%02x", buf[i]);
    printf(":\n");
}

static void print_u64_le(uint64_t v) {
    uint8_t buf[8];
    for (int i = 0; i < 8; i++) { buf[i] = v & 0xff; v >>= 8; }
    print_hex(buf, 8);
}

static uint64_t load64_le(const uint8_t s[8]) {
    uint64_t v = 0;
    for (int i = 7; i >= 0; i--) v = (v << 8) | s[i];
    return v;
}

static uint32_t load32_le(const uint8_t s[4]) {
    uint32_t v = 0;
    for (int i = 3; i >= 0; i--) v = (v << 8) | s[i];
    return v;
}

static char *read_line(char *buf, size_t buf_size) {
    if (!fgets(buf, buf_size, stdin)) return NULL;
    size_t len = strlen(buf);
    while (len > 0 && (buf[len-1] == '\n' || buf[len-1] == '\r' || buf[len-1] == ':' || buf[len-1] == ' '))
        buf[--len] = '\0';
    return buf;
}

static size_t read_hex_param(uint8_t *out, size_t out_size) {
    char line[MAX_LINE];
    if (!read_line(line, sizeof(line))) { fprintf(stderr, "unexpected EOF\n"); exit(1); }
    return hex_decode(out, out_size, line);
}

/* ---- dispatch functions ---- */

static void do_crypto_verify16(void) {
    uint8_t a[16], b[16];
    read_hex_param(a, 16); read_hex_param(b, 16);
    printf("%02x:\n", crypto_verify16(a, b));
}

static void do_crypto_verify32(void) {
    uint8_t a[32], b[32];
    read_hex_param(a, 32); read_hex_param(b, 32);
    printf("%02x:\n", crypto_verify32(a, b));
}

static void do_crypto_verify64(void) {
    uint8_t a[64], b[64];
    read_hex_param(a, 64); read_hex_param(b, 64);
    printf("%02x:\n", crypto_verify64(a, b));
}

static void do_crypto_wipe(void) {
    char line[MAX_LINE];
    read_line(line, sizeof(line));
    size_t len = strlen(line);
    size_t bytes = len / 2;
    uint8_t *buf = malloc(bytes ? bytes : 1);
    hex_decode(buf, bytes, line);
    crypto_wipe(buf, bytes);
    print_hex(buf, bytes);
    free(buf);
}

static void do_crypto_chacha20_h(void) {
    uint8_t key[32], in[16], out[32];
    read_hex_param(key, 32); read_hex_param(in, 16);
    crypto_chacha20_h(out, key, in);
    print_hex(out, 32);
}

static void do_crypto_chacha20_djb(void) {
    uint8_t key[32], nonce[8], plain[MAX_LINE], ctr_buf[8];
    read_hex_param(key, 32); read_hex_param(nonce, 8);
    size_t psize = read_hex_param(plain, sizeof(plain));
    read_hex_param(ctr_buf, 8);
    uint8_t *cipher = malloc(psize ? psize : 1);
    uint64_t new_ctr = crypto_chacha20_djb(cipher, plain, psize, key, nonce, load64_le(ctr_buf));
    print_hex(cipher, psize);
    print_u64_le(new_ctr);
    free(cipher);
}

static void do_crypto_chacha20_ietf(void) {
    uint8_t key[32], nonce[12], plain[MAX_LINE], ctr_buf[4];
    read_hex_param(key, 32); read_hex_param(nonce, 12);
    size_t psize = read_hex_param(plain, sizeof(plain));
    read_hex_param(ctr_buf, 4);
    uint8_t *cipher = malloc(psize ? psize : 1);
    uint32_t new_ctr = crypto_chacha20_ietf(cipher, plain, psize, key, nonce, load32_le(ctr_buf));
    print_hex(cipher, psize);
    uint8_t ncb[4];
    for (int i = 0; i < 4; i++) { ncb[i] = new_ctr & 0xff; new_ctr >>= 8; }
    print_hex(ncb, 4);
    free(cipher);
}

static void do_crypto_chacha20_x(void) {
    uint8_t key[32], nonce[24], plain[MAX_LINE], ctr_buf[8];
    read_hex_param(key, 32); read_hex_param(nonce, 24);
    size_t psize = read_hex_param(plain, sizeof(plain));
    read_hex_param(ctr_buf, 8);
    uint8_t *cipher = malloc(psize ? psize : 1);
    uint64_t new_ctr = crypto_chacha20_x(cipher, plain, psize, key, nonce, load64_le(ctr_buf));
    print_hex(cipher, psize);
    print_u64_le(new_ctr);
    free(cipher);
}

static void do_crypto_poly1305(void) {
    uint8_t key[32], msg[MAX_LINE], mac[16];
    read_hex_param(key, 32);
    size_t msize = read_hex_param(msg, sizeof(msg));
    crypto_poly1305(mac, msg, msize, key);
    print_hex(mac, 16);
}

static void do_crypto_aead_lock(void) {
    uint8_t key[32], nonce[24], ad[MAX_LINE], pt[MAX_LINE];
    read_hex_param(key, 32); read_hex_param(nonce, 24);
    size_t ad_size = read_hex_param(ad, sizeof(ad));
    size_t pt_size = read_hex_param(pt, sizeof(pt));
    uint8_t *ct = malloc(pt_size ? pt_size + 16 : 16);
    crypto_aead_lock(ct + 16, ct, key, nonce, ad, ad_size, pt, pt_size);
    print_hex(ct + 16, pt_size);
    print_hex(ct, 16);
    free(ct);
}

static void do_crypto_aead_unlock(void) {
    uint8_t key[32], nonce[24], ad[MAX_LINE], ct[MAX_LINE], mac[16];
    read_hex_param(key, 32); read_hex_param(nonce, 24);
    size_t ad_size = read_hex_param(ad, sizeof(ad));
    size_t ct_size = read_hex_param(ct, sizeof(ct));
    read_hex_param(mac, 16);
    uint8_t *pt = malloc(ct_size ? ct_size : 1);
    int r = crypto_aead_unlock(pt, mac, key, nonce, ad, ad_size, ct, ct_size);
    if (r == 0) print_hex(pt, ct_size);
    uint8_t rv = (uint8_t)r;
    print_hex(&rv, 1);
    free(pt);
}

static void do_crypto_blake2b(void) {
    uint8_t msg[MAX_LINE], hash[64];
    size_t msize = read_hex_param(msg, sizeof(msg));
    crypto_blake2b(hash, 64, msg, msize);
    print_hex(hash, 64);
}

static void do_crypto_blake2b_keyed(void) {
    uint8_t msg[MAX_LINE], key[256], hash[64];
    size_t msize = read_hex_param(msg, sizeof(msg));
    size_t ksize = read_hex_param(key, sizeof(key));
    if (ksize > 64) ksize = 64;
    crypto_blake2b_keyed(hash, 64, key, ksize, msg, msize);
    print_hex(hash, 64);
}

static void do_crypto_sha512(void) {
    uint8_t msg[MAX_LINE], hash[64];
    size_t msize = read_hex_param(msg, sizeof(msg));
    crypto_sha512(hash, msg, msize);
    print_hex(hash, 64);
}

static void do_crypto_sha512_hmac(void) {
    uint8_t key[256], msg[MAX_LINE], hmac[64];
    size_t ksize = read_hex_param(key, sizeof(key));
    size_t msize = read_hex_param(msg, sizeof(msg));
    crypto_sha512_hmac(hmac, key, ksize, msg, msize);
    print_hex(hmac, 64);
}

static void do_crypto_sha512_hkdf(void) {
    uint8_t ikm[256], salt[256], info[256], okm[256];
    size_t ikm_size  = read_hex_param(ikm,  sizeof(ikm));
    size_t salt_size = read_hex_param(salt, sizeof(salt));
    size_t info_size = read_hex_param(info, sizeof(info));
    char line[MAX_LINE];
    read_line(line, sizeof(line));
    size_t okm_size = strlen(line) / 2;
    if (okm_size > sizeof(okm)) { fprintf(stderr, "okm too large\n"); exit(1); }
    hex_decode(okm, sizeof(okm), line);
    uint8_t *okm_out = malloc(okm_size ? okm_size : 1);
    crypto_sha512_hkdf(okm_out, okm_size, ikm, ikm_size, salt, salt_size, info, info_size);
    print_hex(okm_out, okm_size);
    free(okm_out);
}

static void do_crypto_argon2(void) {
    uint8_t algo_b[4], blocks_b[4], passes_b[4], lanes_b[4];
    read_hex_param(algo_b, 4); read_hex_param(blocks_b, 4);
    read_hex_param(passes_b, 4); read_hex_param(lanes_b, 4);
    uint8_t pass[256], salt[256], key[256], ad[256];
    size_t pass_size = read_hex_param(pass, sizeof(pass));
    size_t salt_size = read_hex_param(salt, sizeof(salt));
    size_t key_size  = read_hex_param(key,  sizeof(key));
    size_t ad_size   = read_hex_param(ad,   sizeof(ad));
    char line[MAX_LINE];
    read_line(line, sizeof(line));
    size_t hash_size = strlen(line) / 2;

    crypto_argon2_config config = { load32_le(algo_b), load32_le(blocks_b),
                                    load32_le(passes_b), load32_le(lanes_b) };
    crypto_argon2_inputs inputs = { pass, salt, (uint32_t)pass_size, (uint32_t)salt_size };
    crypto_argon2_extras extras = { key, ad, (uint32_t)key_size, (uint32_t)ad_size };

    void *work = calloc(load32_le(blocks_b), 1024);
    uint8_t *hash = malloc(hash_size ? hash_size : 1);
    crypto_argon2(hash, (uint32_t)hash_size, work, config, inputs, extras);
    print_hex(hash, hash_size);
    free(work); free(hash);
}

static void do_crypto_x25519(void) {
    uint8_t sk[32], pk[32], shared[32];
    read_hex_param(sk, 32); read_hex_param(pk, 32);
    crypto_x25519(shared, sk, pk);
    print_hex(shared, 32);
}

static void do_crypto_x25519_public_key(void) {
    uint8_t sk[32], pk[32];
    read_hex_param(sk, 32);
    crypto_x25519_public_key(pk, sk);
    print_hex(pk, 32);
}

static void do_crypto_x25519_inverse(void) {
    uint8_t sk[32], point[32], blind[32];
    read_hex_param(sk, 32); read_hex_param(point, 32);
    crypto_x25519_inverse(blind, sk, point);
    print_hex(blind, 32);
}

static void do_crypto_x25519_dirty_small(void) {
    uint8_t sk[32], pk[32];
    read_hex_param(sk, 32);
    crypto_x25519_dirty_small(pk, sk);
    print_hex(pk, 32);
}

static void do_crypto_x25519_dirty_fast(void) {
    uint8_t sk[32], pk[32];
    read_hex_param(sk, 32);
    crypto_x25519_dirty_fast(pk, sk);
    print_hex(pk, 32);
}

static void do_crypto_eddsa_key_pair(void) {
    uint8_t seed[32], sk[64], pk[32];
    read_hex_param(seed, 32);
    crypto_eddsa_key_pair(sk, pk, seed);
    print_hex(sk, 64); print_hex(pk, 32);
}

static void do_crypto_eddsa_sign(void) {
    uint8_t sk[64], pk[32], msg[MAX_LINE], sig[64];
    read_hex_param(sk, 64); read_hex_param(pk, 32);
    size_t msize = read_hex_param(msg, sizeof(msg));
    uint8_t fat_sk[64];
    memcpy(fat_sk, sk, 32); memcpy(fat_sk + 32, pk, 32);
    crypto_eddsa_sign(sig, fat_sk, msg, msize);
    print_hex(sig, 64);
}

static void do_crypto_eddsa_check(void) {
    uint8_t sig[64], pk[32], msg[MAX_LINE];
    read_hex_param(sig, 64); read_hex_param(pk, 32);
    size_t msize = read_hex_param(msg, sizeof(msg));
    uint8_t rv = (uint8_t)crypto_eddsa_check(sig, pk, msg, msize);
    print_hex(&rv, 1);
}

static void do_crypto_ed25519_key_pair(void) {
    uint8_t seed[32], sk[64], pk[32];
    read_hex_param(seed, 32);
    crypto_ed25519_key_pair(sk, pk, seed);
    print_hex(sk, 64); print_hex(pk, 32);
}

static void do_crypto_ed25519_sign(void) {
    uint8_t sk[64], pk[32], msg[MAX_LINE], sig[64];
    read_hex_param(sk, 64); read_hex_param(pk, 32);
    size_t msize = read_hex_param(msg, sizeof(msg));
    uint8_t fat_sk[64];
    memcpy(fat_sk, sk, 32); memcpy(fat_sk + 32, pk, 32);
    crypto_ed25519_sign(sig, fat_sk, msg, msize);
    print_hex(sig, 64);
}

static void do_crypto_ed25519_check(void) {
    uint8_t sig[64], pk[32], msg[MAX_LINE];
    read_hex_param(sig, 64); read_hex_param(pk, 32);
    size_t msize = read_hex_param(msg, sizeof(msg));
    uint8_t rv = (uint8_t)crypto_ed25519_check(sig, pk, msg, msize);
    print_hex(&rv, 1);
}

static void do_crypto_ed25519_ph_sign(void) {
    uint8_t sk[64], pk[32], hash[64], sig[64];
    read_hex_param(sk, 64); read_hex_param(pk, 32);
    read_hex_param(hash, 64);
    uint8_t fat_sk[64];
    memcpy(fat_sk, sk, 32); memcpy(fat_sk + 32, pk, 32);
    crypto_ed25519_ph_sign(sig, fat_sk, hash);
    print_hex(sig, 64);
}

static void do_crypto_ed25519_ph_check(void) {
    uint8_t sig[64], pk[32], hash[64];
    read_hex_param(sig, 64); read_hex_param(pk, 32);
    read_hex_param(hash, 64);
    uint8_t rv = (uint8_t)crypto_ed25519_ph_check(sig, pk, hash);
    print_hex(&rv, 1);
}

static void do_crypto_elligator_map(void) {
    uint8_t hidden[32], curve[32];
    read_hex_param(hidden, 32);
    crypto_elligator_map(curve, hidden);
    print_hex(curve, 32);
}

static void do_crypto_elligator_rev(void) {
    uint8_t point[32], hidden[32];
    read_hex_param(point, 32);
    char line[MAX_LINE];
    read_line(line, sizeof(line));
    uint8_t tweak = (uint8_t)strtol(line, NULL, 16);
    int r = crypto_elligator_rev(hidden, point, tweak);
    if (r == 0) print_hex(hidden, 32);
    uint8_t rv = (uint8_t)r;
    print_hex(&rv, 1);
}

static void do_crypto_elligator_key_pair(void) {
    uint8_t seed[32], r[32], sk[32];
    read_hex_param(seed, 32);
    crypto_elligator_key_pair(r, sk, seed);
    print_hex(r, 32); print_hex(sk, 32);
}

static void do_crypto_eddsa_to_x25519(void) {
    uint8_t eddsa[32], x25519[32];
    read_hex_param(eddsa, 32);
    crypto_eddsa_to_x25519(x25519, eddsa);
    print_hex(x25519, 32);
}

static void do_crypto_x25519_to_eddsa(void) {
    uint8_t x[32], ed[32];
    read_hex_param(x, 32);
    crypto_x25519_to_eddsa(ed, x);
    print_hex(ed, 32);
}

static void do_crypto_aead_init_x(void) {
    uint8_t key[32], nonce[24];
    read_hex_param(key, 32); read_hex_param(nonce, 24);
    crypto_aead_ctx ctx;
    crypto_aead_init_x(&ctx, key, nonce);
    print_hex((uint8_t*)&ctx, sizeof(ctx));
}

static void do_crypto_aead_init_djb(void) {
    uint8_t key[32], nonce[8];
    read_hex_param(key, 32); read_hex_param(nonce, 8);
    crypto_aead_ctx ctx;
    crypto_aead_init_djb(&ctx, key, nonce);
    print_hex((uint8_t*)&ctx, sizeof(ctx));
}

static void do_crypto_aead_init_ietf(void) {
    uint8_t key[32], nonce[12];
    read_hex_param(key, 32); read_hex_param(nonce, 12);
    crypto_aead_ctx ctx;
    crypto_aead_init_ietf(&ctx, key, nonce);
    print_hex((uint8_t*)&ctx, sizeof(ctx));
}

static void do_crypto_aead_write(void) {
    uint8_t key[32], nonce[12], ad[MAX_LINE], pt[MAX_LINE];
    read_hex_param(key, 32); read_hex_param(nonce, 12);
    size_t ad_size = read_hex_param(ad, sizeof(ad));
    size_t pt_size = read_hex_param(pt, sizeof(pt));
    crypto_aead_ctx ctx;
    crypto_aead_init_ietf(&ctx, key, nonce);
    uint8_t *ct = malloc(pt_size ? pt_size : 1);
    uint8_t mac[16];
    crypto_aead_write(&ctx, ct, mac, ad, ad_size, pt, pt_size);
    print_hex(ct, pt_size);
    print_hex(mac, 16);
    free(ct);
}

static void do_crypto_eddsa_trim_scalar(void) {
    uint8_t in[32], out[32];
    read_hex_param(in, 32);
    crypto_eddsa_trim_scalar(out, in);
    print_hex(out, 32);
}

static void do_crypto_eddsa_reduce(void) {
    uint8_t expanded[64], reduced[32];
    read_hex_param(expanded, 64);
    crypto_eddsa_reduce(reduced, expanded);
    print_hex(reduced, 32);
}

static void do_crypto_eddsa_mul_add(void) {
    uint8_t r[32], a[32], b[32], c[32];
    read_hex_param(a, 32); read_hex_param(b, 32); read_hex_param(c, 32);
    crypto_eddsa_mul_add(r, a, b, c);
    print_hex(r, 32);
}

static void do_crypto_eddsa_scalarbase(void) {
    uint8_t scalar[32], point[32];
    read_hex_param(scalar, 32);
    crypto_eddsa_scalarbase(point, scalar);
    print_hex(point, 32);
}

static void do_crypto_eddsa_check_equation(void) {
    uint8_t sig[64], pk[32], hram[32];
    read_hex_param(sig, 64); read_hex_param(pk, 32); read_hex_param(hram, 32);
    uint8_t rv = (uint8_t)crypto_eddsa_check_equation(sig, pk, hram);
    print_hex(&rv, 1);
}

/* ---- dispatch table ---- */

typedef struct { const char *name; void (*func)(void); } dispatch_entry;

static dispatch_entry dispatch_table[] = {
    {"crypto_verify16",             do_crypto_verify16},
    {"crypto_verify32",             do_crypto_verify32},
    {"crypto_verify64",             do_crypto_verify64},
    {"crypto_wipe",                 do_crypto_wipe},
    {"crypto_chacha20_h",           do_crypto_chacha20_h},
    {"crypto_chacha20_djb",         do_crypto_chacha20_djb},
    {"crypto_chacha20_ietf",        do_crypto_chacha20_ietf},
    {"crypto_chacha20_x",           do_crypto_chacha20_x},
    {"crypto_poly1305",             do_crypto_poly1305},
    {"crypto_aead_lock",            do_crypto_aead_lock},
    {"crypto_aead_unlock",          do_crypto_aead_unlock},
    {"crypto_blake2b",              do_crypto_blake2b},
    {"crypto_blake2b_keyed",        do_crypto_blake2b_keyed},
    {"crypto_sha512",               do_crypto_sha512},
    {"crypto_sha512_hmac",          do_crypto_sha512_hmac},
    {"crypto_sha512_hkdf",          do_crypto_sha512_hkdf},
    {"crypto_argon2",               do_crypto_argon2},
    {"crypto_x25519",               do_crypto_x25519},
    {"crypto_x25519_public_key",    do_crypto_x25519_public_key},
    {"crypto_x25519_inverse",       do_crypto_x25519_inverse},
    {"crypto_x25519_dirty_small",   do_crypto_x25519_dirty_small},
    {"crypto_x25519_dirty_fast",    do_crypto_x25519_dirty_fast},
    {"crypto_eddsa_key_pair",       do_crypto_eddsa_key_pair},
    {"crypto_eddsa_sign",           do_crypto_eddsa_sign},
    {"crypto_eddsa_check",          do_crypto_eddsa_check},
    {"crypto_eddsa_trim_scalar",    do_crypto_eddsa_trim_scalar},
    {"crypto_eddsa_reduce",         do_crypto_eddsa_reduce},
    {"crypto_eddsa_mul_add",        do_crypto_eddsa_mul_add},
    {"crypto_eddsa_scalarbase",     do_crypto_eddsa_scalarbase},
    {"crypto_eddsa_check_equation", do_crypto_eddsa_check_equation},
    {"crypto_ed25519_key_pair",     do_crypto_ed25519_key_pair},
    {"crypto_ed25519_sign",         do_crypto_ed25519_sign},
    {"crypto_ed25519_check",        do_crypto_ed25519_check},
    {"crypto_ed25519_ph_sign",      do_crypto_ed25519_ph_sign},
    {"crypto_ed25519_ph_check",     do_crypto_ed25519_ph_check},
    {"crypto_elligator_map",        do_crypto_elligator_map},
    {"crypto_elligator_rev",        do_crypto_elligator_rev},
    {"crypto_elligator_key_pair",   do_crypto_elligator_key_pair},
    {"crypto_eddsa_to_x25519",      do_crypto_eddsa_to_x25519},
    {"crypto_x25519_to_eddsa",      do_crypto_x25519_to_eddsa},
    {"crypto_aead_init_x",          do_crypto_aead_init_x},
    {"crypto_aead_init_djb",        do_crypto_aead_init_djb},
    {"crypto_aead_init_ietf",       do_crypto_aead_init_ietf},
    {"crypto_aead_write",           do_crypto_aead_write},
    {NULL, NULL}
};

int main(int argc, char **argv) {
    (void)argc; (void)argv;

    char func_name[256];
    if (!read_line(func_name, sizeof(func_name))) {
        fprintf(stderr, "empty input\n");
        return 1;
    }

    for (dispatch_entry *d = dispatch_table; d->name; d++) {
        if (strcmp(func_name, d->name) == 0) {
            d->func();
            return 0;
        }
    }

    fprintf(stderr, "unknown function: %s\n", func_name);
    return 1;
}
