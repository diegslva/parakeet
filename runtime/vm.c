#include <stdio.h>
#include <stdlib.h>

typedef struct {
  double *a;
  double *b;
  double *out;
  int     m;
  int     n;
  int     k;
} vm_args_t;

double *make_array(int m, int n) {
  double *array = (double*)malloc(m * n * sizeof(double));
  int i;
  for (i = 0; i < m * n; ++i) {
    array[i] = ((double)m) / n;
  }
  return array;
}

void free_array(double *array) {
  free(array);
}

void vm(int start, int end, void *args, int *tile_sizes) {
  vm_args_t *my_args = (vm_args_t*)args;
  double *A = my_args->a;
  double *B = my_args->b;
  double *O = my_args->out;
  int m = my_args->m;
  int n = my_args->n;
  int k = my_args->k;
  int l3bLen, l2aLen, l2bLen, l1aLen, l1bLen;
  int i, j, l;
  int aOff, bOff, oOff;

  l3bLen = tile_sizes[0];
  l2aLen = tile_sizes[1];
  l2bLen = tile_sizes[2];
  l1aLen = tile_sizes[3];
  l1bLen = tile_sizes[4];
  int l3b, l2a, l2b, l2as, l2bs, l1a, l1b, l1as, l1bs;
  int is, js;
  // l3a tiling amounts to size of chunk
  for (l3b = 0; l3b < n; l3b += l3bLen) {
    for (l2a = start; l2a < end; l2a += l2aLen) {
      l2bs = l3b + l3bLen;
      if (l2bs > n) l2bs = n;
      for (l2b = l3b; l2b < l2bs; l2b += l2bLen) {
        l1as = l2a + l2aLen;
        if (l1as > m) l1as = m;
        for (l1a = l2a; l1a < l1as; l1a += l1aLen) {
          l1bs = l2b + l2bLen;
          if (l1bs > n) l1bs = n;
          for (l1b = l2b; l1b < l1bs; l1b += l1bLen) {
            is = l1a + l1aLen;
            if (is > m) is = m;
            for (i = l1a; i < is; ++i) {
              aOff = i * k;
              oOff = i * n;
              js = l1b + l1bLen;
              if (js > n) js = n;
              for (j = l1b; j < js; ++j) {
                bOff = j * k;
                O[oOff + j] = 0.0;
                for (l = 0; l < k; ++l) {
                  O[oOff + j] += A[aOff + l] * B[bOff + l];
                }
              }
            }
          }
        }
      }
    }
  }
}

static inline int min(a, b) {
  return a < b ? a : b;
}

void vm2(int start, int end, void *args, int *tile_sizes) {
  vm_args_t *my_args = (vm_args_t*)args;
  double *A = my_args->a;
  double *B = my_args->b;
  double *O = my_args->out;
  int m = my_args->m;
  int n = my_args->n;
  int k = my_args->k;
  int i, j, l;
  int aOff, bOff, oOff;

  int l2b, l1a, l1b, l1as, l1bs;
  int l2bLen, l1aLen, l1bLen;
  l2bLen = tile_sizes[0];
  l1aLen = tile_sizes[1];
  l1bLen = tile_sizes[2];
  int is, js;
  for (l2b = 0; l2b < n; l2b += l2bLen) {
    for (l1a = start; l1a < end; l1a += l1aLen) {
      l1bs = l2b + l2bLen;
      if (l1bs > n) l1bs = n;
      for (l1b = l2b; l1b < l1bs; l1b += l1bLen) {
        is = l1a + l1aLen;
        if (is > m) is = m;
        for (i = l1a; i < is; ++i) {
          aOff = i * k;
          oOff = i * n;
          js = l1b + l1bLen;
          if (js > n) js = n;
          for (j = l1b; j < js; ++j) {
            bOff = j * k;
            O[oOff + j] = 0.0;
            for (l = 0; l < k; ++l) {
              O[oOff + j] += A[aOff + l] * B[bOff + l];
            }
          }
        }
      }
    }
  }
}

void vm3(int start, int end, void *args, int *tile_sizes) {
  vm_args_t *my_args = (vm_args_t*)args;
  double *A = my_args->a;
  double *B = my_args->b;
  double *O = my_args->out;
  int m = my_args->m;
  int n = my_args->n;
  int k = my_args->k;
  int i, j, l;
  int aOff, bOff, oOff;

  int l1bLen = tile_sizes[0];
  int l1b;
  int is, js;
  for (l1b = 0; l1b < n; l1b += l1bLen) {
    for (i = start; i < end; ++i) {
      aOff = i * k;
      oOff = i * n;
      js = l1b + l1bLen;
      if (js > n) js = n;
      for (j = l1b; j < js; ++j) {
        bOff = j * k;
        O[oOff + j] = 0.0;
        for (l = 0; l < k; ++l) {
          O[oOff + j] += A[aOff + l] * B[bOff + l];
        }
      }
    }
  }
}

// mu = 6, nu = 1, no unrolling of ku loop
void vm4(int start, int end, void *args, int *tile_sizes) {
  vm_args_t *my_args = (vm_args_t*)args;
  double *A = my_args->a;
  double *B = my_args->b;
  double *O = my_args->out;
  int m = my_args->m;
  int n = my_args->n;
  int kLen = my_args->k;
  int aOff, bOff, oOff;

  int l1bLen = tile_sizes[0];
  int l1cLen = tile_sizes[1];
  int ku = tile_sizes[2];
  int j, k, i2, j2, k2, k3;
  int it, jt;
  for (j = 0; j < n; j += l1bLen) {
    int j2End = min(j + l1bLen, n);
    for (it = start; it < end; ++it) {
      for (jt = j; jt < j2End; ++jt) {
        O[it*n + jt] = 0.0;
      }
    }
    for (k = 0; k < kLen; k += l1cLen) {
      int k2End = min(k + l1cLen, kLen);
      for (i2 = start; i2 < end; ++i2) {
        aOff = i2*kLen;
        oOff = i2*n;
        for (j2 = j; j2 < j2End; j2 += 6) {
          bOff = j2*kLen;
          double c0, c1, c2, c3, c4, c5;
          c0 = c1 = c2 = c3 = c4 = c5 = 0.0;
          for (k3 = k; k3 < k2End; ++k3) {
            double a0;
            double b0, b1, b2, b3, b4, b5;
//            int k3End = min(k2 + ku, kLen);
//            for (k3 = k2; k3 < k3End; ++k3) {
              a0 = A[aOff + k3];
              b0 = B[bOff + k3];
              b1 = B[bOff + kLen + k3];
              b2 = B[bOff + 2 * kLen + k3];
              b3 = B[bOff + 3 * kLen + k3];
              b4 = B[bOff + 4 * kLen + k3];
              b5 = B[bOff + 5 * kLen + k3];
              c0 += a0 * b0;
              c1 += a0 * b1;
              c2 += a0 * b2;
              c3 += a0 * b3;
              c4 += a0 * b4;
              c5 += a0 * b5;
//            }
          }
          O[oOff + j2] += c0;
          O[oOff + j2 + 1] += c1;
          O[oOff + j2 + 2] += c2;
          O[oOff + j2 + 3] += c3;
          O[oOff + j2 + 4] += c4;
          O[oOff + j2 + 5] += c5;
        }
      }
    }
  }
}

// mu = 6, nu = 1, no unrolling of ku loop
void vm5(int start, int end, void *args, int *tile_sizes) {
  vm_args_t *my_args = (vm_args_t*)args;
  double *A = my_args->a;
  double *B = my_args->b;
  double *O = my_args->out;
  int m = my_args->m;
  int n = my_args->n;
  int kLen = my_args->k;
  int aOff, bOff, oOff;

  int l1bLen = tile_sizes[0];
  int l1cLen = tile_sizes[1];
  int ku = tile_sizes[2];
  int j, k, i2, j2, k2, k3;
  int it, jt;
  for (j = 0; j < n; j += l1bLen) {
    int j2End = min(j + l1bLen, n);
    for (i2 = start; i2 < end; ++i2) {
      aOff = i2*kLen;
      oOff = i2*n;
      for (j2 = j; j2 < j2End; j2 += 6) {
        bOff = j2*kLen;
        double c0, c1, c2, c3, c4, c5;
        c0 = c1 = c2 = c3 = c4 = c5 = 0.0;
        for (k3 = 0; k3 < kLen; ++k3) {
          double a0;
          double b0, b1, b2, b3, b4, b5;
          a0 = A[aOff + k3];
          b0 = B[bOff + k3];
          b1 = B[bOff + kLen + k3];
          b2 = B[bOff + 2 * kLen + k3];
          b3 = B[bOff + 3 * kLen + k3];
          b4 = B[bOff + 4 * kLen + k3];
          b5 = B[bOff + 5 * kLen + k3];
          c0 += a0 * b0;
          c1 += a0 * b1;
          c2 += a0 * b2;
          c3 += a0 * b3;
          c4 += a0 * b4;
          c5 += a0 * b5;
        }
        O[oOff + j2] = c0;
        O[oOff + j2 + 1] = c1;
        O[oOff + j2 + 2] = c2;
        O[oOff + j2 + 3] = c3;
        O[oOff + j2 + 4] = c4;
        O[oOff + j2 + 5] = c5;
      }
    }
  }
}

void vm_handgen(int start, int end, void *args, int *tile_sizes) {
  vm_args_t *my_args = (vm_args_t*)args;
  double *A = my_args->a;
  double *B = my_args->b;
  double *O = my_args->out;
  int m = my_args->m;
  int n = my_args->n;
  int kLen = my_args->k;
  int aOff, bOff, oOff;

  int l1bLen = tile_sizes[0];
  int l1cLen = tile_sizes[1];

  // A L1 tile is implicit as the start/end of the chunk.
  int j;
  for (j = 0; j < n; j += l1bLen) {
    int j2End = min(j + l1bLen, n);
    double *Btile = B + j*kLen;
    int it;
    for (it = start; it < end; ++it) {
      double *Otile = O + it*n;
      int jt;
      for (jt = j; jt < j2End; ++jt) {
        Otile[jt] = 0.0;
      }
    }
    int k;
    for (k = 0; k < kLen; k += l1cLen) {
      int k3End = min(k + l1cLen, kLen);
      int i2;
      // A's reg tile size set to 1.
      for (i2 = start; i2 < end; ++i2) {
        double *Arow = A + i2*kLen;
        double *Orow = O + i2*n;
        int j2;
        // B's reg tile size set to 6.
        for (j2 = j; j2 < j2End; j2 += 6) {
          double *Brow = B + j2*kLen;
          double *Ocol = Orow + j2;
          double c0, c1, c2, c3, c4, c5;
          c0 = c1 = c2 = c3 = c4 = c5 = 0.0;
          int k3;
          for (k3 = k; k3 < k3End; ++k3) {
            double a0 = Arow[k3];
            double b0 = Brow[k3];
            double b1 = Brow[kLen + k3];
            double b2 = Brow[2*kLen + k3];
            double b3 = Brow[3*kLen + k3];
            double b4 = Brow[4*kLen + k3];
            double b5 = Brow[5*kLen + k3];
            c0 = c0 + (a0 * b0);
            c1 = c1 + (a0 * b1);
            c2 = c2 + (a0 * b2);
            c3 = c3 + (a0 * b3);
            c4 = c4 + (a0 * b4);
            c5 = c5 + (a0 * b5);
          }
          Ocol[0*n + 0] = Ocol[0*n + 0] + c0;
          Ocol[0*n + 1] = Ocol[0*n + 1] + c1;
          Ocol[0*n + 2] = Ocol[0*n + 2] + c2;
          Ocol[0*n + 3] = Ocol[0*n + 3] + c3;
          Ocol[0*n + 4] = Ocol[0*n + 4] + c4;
          Ocol[0*n + 5] = Ocol[0*n + 5] + c5;
        }
      }
    }
  }
}
