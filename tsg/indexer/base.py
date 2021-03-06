import math
import glob
import logging
import re
import json

import pandas as pd
import numpy as np

from tsg.config import FIELD_WEIGHTS


def parse_term(term_file, N, qscores, pagerank_scores):
    '''
    N: number of documents in total
    '''
    term_df = pd.read_csv(term_file, index_col='uuid')

    # count per document
    weighted_sum = (term_df*FIELD_WEIGHTS).sum(axis=1)
    log_weights = (np.log10(weighted_sum)+1)
    df_qscores = term_df.apply(lambda row: qscores.loc[row.name].qscore,
                                axis=1)
    df_pagerank_scores = term_df.apply(lambda row: pagerank_scores.loc[row.name].pagerank_score,
                                       axis=1)

    # log page rank scores and move minimum to 1
    df_pagerank_scores = np.log10(df_pagerank_scores)
    df_pagerank_scores += 1 - np.min(df_pagerank_scores)

    term_df['tf-idf'] = \
        log_weights * \
        df_qscores * \
        df_pagerank_scores * \
        (1+math.log10(N/len(term_df)))

    term_df.sort_values('tf-idf', ascending=False, inplace=True)

    pairs = term_df.apply(lambda row: '{}:{}'.
                          format(row.name, row['tf-idf']),
                          axis=1)
    return ",".join(pairs)


def create_index(intermediate_dir,
                 parsed_dir,
                 num_documents,
                 dictionary_path,
                 indexinfo_path,
                 qscore_path,
                 pagerank_path):

    log_cnt = 0

    # calculate quality scores
    qscores = pd.read_csv(qscore_path, index_col='uuid')

    # load pagerank
    pagerank_scores = pd.read_csv(pagerank_path, index_col='uuid')

    # find all csvs and sort them alphabetically
    files = glob.glob(intermediate_dir+'*.csv')
    files.sort()

    compiled_termname_re = re.compile('([^/]*).csv')
    with open(dictionary_path, 'w') as dictionary_file:  # deletes dictionary!
        for term_file in files:
            term = compiled_termname_re.search(term_file).groups()[0]
            indexed_line = parse_term(term_file,
                                      num_documents,
                                      qscores,
                                      pagerank_scores)

            dictionary_file.write('{} {}\n'.format(term, indexed_line))
            logging.info('Indexed term {}'.format(term))

            if log_cnt % 1000000 == 0:
                logging.info('created index-line for {} files'.format(log_cnt))
            log_cnt += 1

    create_indexinfo(num_documents, indexinfo_path)


def create_indexinfo(num_documents, indexinfo_path):
    obj = {'num_documents': num_documents}
    with open(indexinfo_path, 'w') as f:
        json.dump(obj, f)


def hash_index():
    pass
