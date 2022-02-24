import sys
import pprint

from googleapiclient.discovery import build

MAX_ITERATIONS = 1


def google_search(api_key, engine_id, query, **kwargs):

    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=engine_id, **kwargs).execute()
    # print(type(res["items"]))
    # print(res.keys())
    return res['items']


def main():
    if (len(sys.argv) != 5 or float(sys.argv[3]) > 1
            or float(sys.argv[3]) < 0):
        print("Usage: main.py <google api key> <google engine id> <precision> <query>")
        print("Also, <precision> should be between 0 and 1")
    else:
        print("google api key: " + sys.argv[1])
        print("google engine id: " + sys.argv[2])
        print("precision: " + sys.argv[3])
        print("query: " + sys.argv[4])

    api_key, engine_id, desired_precision, query = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    google_search(api_key, engine_id, query, num=5)
    for i in range(MAX_ITERATIONS):
        results = google_search(api_key, engine_id, query, num=10)
        print('Google Search Results:')
        print('======================')
        # print("results: ", type(results))

        total, relevent, non_relevent = 0, 0, 0
        relevent_lst = []
        non_relevent_lst = []

        for i, item in enumerate(results):
            total += 1
            url = item['formattedUrl']
            if 'title' not in item:
                title = ''
            else:
                title = item['title']
            if 'snippet' not in item:
                description = ''
            else:
                description = item['snippet'].replace('\n', '').replace('\xa0', '')
            print("snippet is: ", item['snippet'])

            # # fullpage
            #
            # print(f'Result {i + 1}')
            # print('[')
            # print(f'URL: {url}')
            # print(f'Title: {title}')
            # print(f'Description: {description}')
            # print(']')
            # print()
            # answer = input('Relevant (Y/N)?')
            #
            # if (answer == "Y" or answer == "y"):
            #     relevent += 1
            #     relevent_lst.append(title)
            # else:
            #     non_relevent += 1
            #     non_relevent_lst.append(title)

        print(relevent_lst)
        print(non_relevent_lst)

        # TODO augment queries (add two words)


if __name__ == '__main__':
    main()