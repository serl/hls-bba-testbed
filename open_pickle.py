import pickle, sys
import matplotlib.pyplot as plt

with open(sys.argv[1], 'r') as f:
	fig = pickle.load(f)
	plt.show()

