import sys
import numpy as np
from googleapiclient.discovery import build
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

MAX_ITERATIONS = 10
ALPHA = 1
BETA = 0.75
GAMMA = 0.15

# get search results from google search engine
def google_search(api_key, engine_id, query, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=engine_id, **kwargs).execute()
    return res['items']


# print input parameters
def print_parameters(api_key, engine_id, desired_precision, query):
    print('Parameters: ')
    print(f'Client key  = {api_key}')
    print(f'Engine id   = {engine_id}')
    print(f'Precision   = {desired_precision}')
    print(f'Query       = {query}')


# augment current query by Rocchio algorithm
def augment_query(relevant_docs, non_relevant_docs, query):
    query_words = query.split()
    num_words = len(query_words)
    documents, query = relevant_docs + non_relevant_docs, [query]
    num_relevant_docs, num_non_relevant_docs = len(relevant_docs), len(non_relevant_docs)

    # initialize TF_IDF Vectorizer
    tfidf_vectorizer = TfidfVectorizer(analyzer='word', stop_words='english')
    
    # get documents matrix and query vector
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents).toarray()
    q_0_vector = tfidf_vectorizer.transform(query).toarray()

    # get relevant document vectors and non-relevant document vectors
    relevant_vectors = tfidf_vectorizer.transform(relevant_docs).toarray()
    non_relevant_vectors = tfidf_vectorizer.transform(non_relevant_docs).toarray()

    relevant_vectors_sum = sum(relevant_vectors)
    non_relevant_vectors_sum = sum(non_relevant_vectors)

    # update query vectors
    query_vecs = ALPHA * q_0_vector + BETA * 1 / num_relevant_docs * relevant_vectors_sum - GAMMA * 1 / num_non_relevant_docs * non_relevant_vectors_sum
    
    words_dict = tfidf_vectorizer.inverse_transform(query_vecs)[0]
    words_ranking = np.flip(query_vecs.argsort())[0]
    
    new_query_words = []
    left_query_words = list(query_words)
    for i in range(num_words + 2):
        new_word = words_dict[words_ranking[i]]
        new_query_words.append(new_word)
        if new_word in query_words:
            left_query_words.remove(new_word)
    
    num_left_words = len(left_query_words) 
    if num_left_words > 0:
        new_query_words = new_query_words[:-num_left_words] + left_query_words

    new_query = ""
    expanding_words = []
    # print(new_query_words)
    for word in new_query_words:
        new_query += word + " "
        
        if word not in query_words:
            expanding_words.append(word)

    return new_query, expanding_words[0], expanding_words[1]


def main():
    if(len(sys.argv) != 5 or float(sys.argv[3]) > 1 or float(sys.argv[3]) < 0):
        print("Usage: main.py <google api key> <google engine id> <precision> <query>")
        print("Also, <precision> should be between 0 and 1")
    else:
        api_key, engine_id = sys.argv[1], sys.argv[2]
        desired_precision, og_query = float(sys.argv[3]), sys.argv[4]
        print_parameters(api_key, engine_id, desired_precision, og_query)
    
    curr_query = og_query
    for i in range(MAX_ITERATIONS):
        print(f'Iteration #{i+1}')

        results = google_search(api_key, engine_id, curr_query, num=10)
        
        # no results returned, terminate the program
        if (len(results) < 10):
            print('Not enough results are found, done')
            break

        total, num_relevant, num_non_relevant = 0, 0, 0
        relevant_lst = []
        non_relevant_lst = []

        print('Google Search Results:')
        print('======================')
        for i, item in enumerate(results):
            print(f'Result {i+1}')
            total += 1
            url = item['formattedUrl']
            if 'fileFormat' in item.keys():
                print(item['fileFormat'])
            if 'title' not in item:
                title = ''
            else:
                title = item['title']
            if 'snippet' not in item:
                description = ''
            else:
                description = item['snippet'].replace('\n', '').replace('\xa0', '')

            # print each result
            print('[')
            print(f'URL: {url}')
            print(f'Title: {title}')
            print(f'Description: {description}')
            print(']')
            print()

            # get feedback
            answer = input('Relevant (Y/N)?')
            if (answer == "Y" or answer == "y"):
                num_relevant += 1
                relevant_lst.append(title + description)
            else:
                num_non_relevant += 1
                non_relevant_lst.append(title + description) 

        if num_relevant == 0:
            print('Zero results are relevant in the first iteration, done')
            break

        curr_precision = num_relevant / total
        print("FEEDBACK SUMMARY")
        print(f'Current Query : {curr_query}')
        print(f'Current Precision : {curr_precision}')

        # check if desired precision is reached
        if curr_precision < desired_precision:
            print(f'Still below the desired precision of {desired_precision}')
            print('Indexing results ....')
            
            # augment current query by adding two words
            new_query, expanding_word_1, expanding_word_2 = augment_query(relevant_lst, non_relevant_lst, curr_query)
            print(f'Augmenting by {expanding_word_1} {expanding_word_2}')
            curr_query = new_query
            print_parameters(api_key, engine_id, desired_precision, curr_query)
        else:
            print("Desired precision reached, done")
            break
        
if __name__ == '__main__':
    main()