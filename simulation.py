# Script to simulate number of calls before a bingo win

import numpy as np
# import matplotlib.pyplot as plt | opt for plotting and analysis in R, so just export to CSV
import random
import csv


class BingoCard:

	def __init__(self, pool: list, dim: tuple):
		nrow, ncol = dim
		assert len(pool) >= nrow * ncol, f"pool size should be at least {nrow}*{ncol}={nrow*ncol}, but is {len(pool)}"
		self.card = []
		random.shuffle(pool)
		self.wins = 0

		for _ in range(nrow):
			self.card.append(set(pool[:ncol]))
			pool = pool[ncol:]
	
	def __repr__(self):
		return str(self.card)

	def update(self, call):
		for row in self.card:
			if call in row:
				row.remove(call)
				break
		
		self.wins = self.card.count(set())

def simulate(n_cards: int, dim: tuple, pool_max = int, n_wins = int) -> int:
	pool = list(range(pool_max))
	cards = [BingoCard(pool, dim) for _ in range(n_cards)]
	random.shuffle(pool)
	for i, n in enumerate(pool):
		for card in cards:
			card.update(n)
			if card.wins == n_wins:
				return (i+1)

def simulate_batch(n_sim: int, n_cards: int, dim: tuple, pool_max = int, n_wins = int) -> list:
	return [simulate(n_cards, dim, pool_max, n_wins) for _ in range(n_sim)]

# Thanks to SO-user senderle!
def cartesian_product(*arrays):
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[...,i] = a
    return arr.reshape(-1, la)

def main():
	n_sim = 1000
	height = 3
	widths = np.arange(3, 7)
	n_cards = np.arange(10, 101, 10)
	pool_max = np.arange(20, 101, 10)
	n_wins = np.arange(1, 4)

	helper = lambda par : simulate_batch(n_sim, par[1], (height, par[0]), par[2], par[3]) 

	pars = cartesian_product(widths, n_cards, pool_max, n_wins)
	data = []
	par_names = ('width', 'n_cards', 'pool_max', 'n_wins')
	
	for i, par in enumerate(pars):
		print(i / pars.shape[0])
		result = helper(par)
		par_dict = {'n_sim' : n_sim, 'height' : height} | {d[0] : d[1] for d in zip(par_names, par)}
		result_dict = {f'x{i}' : r for i, r in enumerate(result)}
		data.append( par_dict | result_dict)

	with open('simulation_result.csv', 'w', newline='') as csv_file:
		fieldnames = list(par_dict.keys()) + [f'x{i}' for i in range(n_sim)]
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(data)

if __name__ == '__main__':
	main()