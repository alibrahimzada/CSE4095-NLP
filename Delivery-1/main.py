import warnings
warnings.simplefilter('ignore')

import json
import os
import argparse
from typing import Counter
from zemberek import TurkishTokenizer
from frequency import Frequency
from t_test import TTest
from hypothesis_testing_diff import HypothesisTestingDiff
from tqdm import tqdm
from mutual_information import MutualInformation
from diff_mean_variance import DiffMeanVariance
from likelihood_ratios import LikelihoodRatios
from chi_square_test import PearsonChiSquareTest


def parse_data(files, args): # parse the data and return a dictionary
    data = {}
    pbar = tqdm(files)
    for f_name in pbar:
        pbar.set_description(f'parsing: {f_name}')
        with open('data/' + args.raw_data_dir + '/' + f_name, encoding='utf-8') as f:
            f_number = f_name.split('.')[0]
            data[f_number] = json.load(f)['ictihat']

    return data


def export_data(data, args): # clean the data and export it
    tokenizer = TurkishTokenizer.DEFAULT

    pbar = tqdm(data)
    for key in pbar:
        pbar.set_description(f'cleaning file {key}')
        tokens = tokenizer.tokenize(data[key])

        filtered_tokens = []
        for token in tokens:
            if token.type_.name != 'Word': continue # remove anything which is not a word
            if len(token.content) == 1: continue # remove anything which is a single character
            filtered_tokens.append(token.content.lower())

        data[key] = ' '.join(filtered_tokens)

    with open(f'data/{args.f_name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=4)


def export_ngrams(n, args): # export ngrams based on a given value of n
    data = {}
    with open(f'data/{args.f_name}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    ngrams = Counter()
    pbar = tqdm(data)
    for key in pbar:
        pbar.set_description(f'counting {n}-grams for file {key}')
        splitted = data[key].split()
        for i in range(len(splitted)-n+1):
            ngrams.update([' '.join(splitted[i:i+n])])

    with open(f'data/{n}grams_{args.f_name}.json', 'w', encoding='utf-8') as f:
        json.dump(ngrams, f, ensure_ascii=False, sort_keys=True, indent=4)


def main(args):
    if args.clean_data:
        data = parse_data(os.listdir('data/' + args.raw_data_dir), args)
        export_data(data, args)

    elif args.export_ngrams:
        export_ngrams(2, args)
        export_ngrams(3, args)

    else:
        with open(f'data/{args.f_name}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(f'data/2grams_{args.f_name}.json', 'r', encoding='utf-8') as f:
            bigrams = json.load(f)

        with open(f'data/3grams_{args.f_name}.json', 'r', encoding='utf-8') as f:
            trigrams = json.load(f)

        if args.method == 'frequency':
            print('\n===== FREQUENCY =====')
            frequency = Frequency(bigrams, trigrams)
            frequency.export_collocation_by_frequency(type='bigram', n=200)
            frequency.export_collocation_by_frequency(type='trigram', n=200)

        elif args.method == 'pmi':
            print('\n===== PMI =====')
            mutual_information = MutualInformation(data, bigrams)
            mutual_information.export_collocation_by_pmi(n=200)

        elif args.method == 't_test':
            print('\n===== T-TEST =====')
            t_test = TTest(data, bigrams)
            t_test.export_collocation_by_t_test(n=200)

        elif args.method == 'diff_mean_var':
            print('\n===== DIFFERENCE OF MEAN AND VARIANCE =====')
            diff_mean_var = DiffMeanVariance(data)
            diff_mean_var.export_collocation_by_diff_mean_var()

        elif args.method == "hypothesis_testing_diff":
            # we have discarded this method for the time being due to its high computational complexity
            print('\n===== HYPOTHESIS TESTING DIFFERENCE =====')
            ht_diff = HypothesisTestingDiff(bigrams)
            ht_diff.export_collocation_by_hypothesis_testing_diff(n=200)

        elif args.method == 'chi_square':
            print('\n===== CHI SQUARE TEST =====')
            chi_square = PearsonChiSquareTest(data, bigrams)
            chi_square.export_collocations_by_chi_square(n=200)

        elif args.method == "likelihood_ratios":
            print('\n===== LIKELIHOOD RATIOS =====')
            liklihood_ratios = LikelihoodRatios(data, bigrams)
            liklihood_ratios.export_collocation_by_likelihood_ratios(n=200)


def parse_args():
    parser = argparse.ArgumentParser("Collocation Extractor")
    parser.add_argument('--clean_data', type=bool, default=False, help='clean the raw data')
    parser.add_argument('--raw_data_dir', type=str, default='2021-01', help='raw dataset directory')
    parser.add_argument('--f_name', type=str, default='dataset', help='file name')
    parser.add_argument('--export_ngrams', type=bool, default=False, help='export ngrams (i.e., n=2,3,..)')
    parser.add_argument('--method', type=str, default='frequency', help='method to extract collocations')
    
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
