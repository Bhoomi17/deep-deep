#!/usr/bin/env python
import argparse
from itertools import islice
from typing import List, Dict

from eli5.sklearn.explain_weights import explain_weights
from eli5.formatters import format_as_text
from eli5.sklearn.unhashing import InvertableHashingVectorizer
import joblib
import json_lines
from scrapy.http.response.text import TextResponse
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.preprocessing import FunctionTransformer

from deepdeep.links import DictLinkExtractor


def main():
    parser = argparse.ArgumentParser()
    arg = parser.add_argument
    arg('q_model')
    arg('data')
    arg('--limit', type=int)
    arg('--top', type=int, default=100)
    args = parser.parse_args()

    q_model = joblib.load(args.q_model)
    with json_lines.open(args.data) as items:
        if args.limit:
            items = islice(items, args.limit)

        # With a huge number of links it's better
        # to re-read them.
        print('Extracting links...')
        le = DictLinkExtractor()
        links = [
            link for item in items
            for link in extract_links(le, TextResponse(
                url=item['url'],
                body=item['raw_content'],
                encoding='utf8'))]
        print('Done.')

        assert not q_model.get('page_vectorizer'), 'TODO'
        all_features_names = []
        for name, vec in q_model['link_vectorizer'].transformer_list:
            if isinstance(vec, HashingVectorizer):
                print('Fitting inverse vectorizer for {}'.format(vec))
                ivec = InvertableHashingVectorizer(vec)
                ivec.fit(links)
                print('Done, now getting features.')
                vec_name = vec.preprocessor.__name__
                all_features_names.extend(
                    '{} {}'.format(vec_name, feature)
                    for feature in ivec.get_feature_names())
                print('Done.')
            elif isinstance(vec, FunctionTransformer):
                all_features_names.append(vec.func.__name__)

        clf = q_model['Q'].clf_online
        expl = explain_weights(
            clf, feature_names=all_features_names, top=args.top)
        print(format_as_text(expl))


def extract_links(le: DictLinkExtractor, response: TextResponse) -> List[Dict]:
    """ Return a list of all unique links on a page """
    return list(le.iter_link_dicts(
        response=response,
        limit_by_domain=False,
        deduplicate=False,
        deduplicate_local=True,
    ))


if __name__ == '__main__':
    main()