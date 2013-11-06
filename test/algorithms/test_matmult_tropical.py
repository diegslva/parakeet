import parakeet
import parakeet.testing_helpers
import numpy as np 
parakeet.config.print_specialized_function=True

def dot(x,y):
    return parakeet.reduce(min(x+y), axis = 0, init = np.inf)

def matmult_high_level(X,Y):
  return np.array([[dot(x,y) for y in Y.T] for x in X])

def test_matmult_tropical():
  n, d = 4,5
  m = 3
  X = np.random.randn(m,d)
  Y = np.random.randn(d,n)
  parakeet.testing_helpers.expect(matmult_high_level, [X,Y], matmult_high_level(X,Y))

if __name__ == '__main__':
    parakeet.testing_helpers.run_local_tests()


