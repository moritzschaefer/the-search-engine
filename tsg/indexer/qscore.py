''' Calculate quality score for all documents :)'''
import json
import glob
import logging
import numpy as np
from scipy import stats


def get_scores(directory):
    # read all documents, get a distribution for q scores
    cats = ['conference_overview', 'conference', 'author', 'journal']
    counts = {cat: [] for cat in cats}
    doc_counts = {}

    for filename in glob.glob(directory + '/*.json'):
        with open(filename) as f:
            parsed = json.load(f)
            cat = parsed['type']
            if cat == 'conference' and parsed['url'][-5:] != '.html':
                cat = 'conference_overview'

            counts[cat].append(parsed['listings_count'])
            doc_counts[parsed['uuid']] = (parsed['listings_count'], cat)

    logging.debug('Finished scanning documents. Calculate qscores now')

    distributions = {cat: (np.array(counts[cat]).mean(),
                           np.array(counts[cat]).std()) for cat in cats}

    for key in doc_counts:
        count, cat = doc_counts[key]
        doc_counts[key] = _normalized_quality_score(distributions[cat][0],
                                                    distributions[cat][1],
                                                    count)

    return doc_counts


def _normalized_quality_score(mean, std, listings_count):
    if std == 0:
        p = int(listings_count > mean)
    else:
        p = stats.norm.cdf(listings_count, loc=mean, scale=std)
    return (p+2)/3
