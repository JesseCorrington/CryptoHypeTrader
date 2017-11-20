import re
import operator
import basc_py4chan
import urllib.request, json
from textblob import TextBlob


all_coins = []
counts = {}

def get_json(url):
    url = urllib.request.urlopen(url)
    json_data = json.loads(url.read().decode())
    return json_data


def parse_tokens(text):
    tokens = text.split()

    analysis = TextBlob(text)

    for token in tokens:
        token = token.lower()
        if token in counts:
            counts[token]['basic'] += 1

            # TODO: this maybe doesn't make sense since the comment could be about many coins
            counts[token]['sentiment'] += analysis.polarity


def clean_comment(self, comment):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", comment).split())


def read_thread(board, thread_id):
    thread = board.get_thread(thread_id)

    # thread information
    if not thread.sticky:
        # topic information
        topic = thread.topic
        #print('Topic Repr', topic)
        #print('Postnumber', topic.post_number)
        #print('Timestamp', topic.timestamp)
        #print('Datetime', topic.datetime)
        #print('Subject', topic.subject)
        #print('Comment', topic.text_comment)
        #print('Replies', len(thread.replies))

        #TODO: do we want to parse the headings also
        #TODO: we will need some kind of weighting

        parse_tokens(topic.text_comment)

        # TODO: we can prob use a custom lexion on textblob for this
        # TODO: also look for buy or sell in the same thread
        #buy_tokens = {'buy', 'hold', 'long'}
        #sell_tokens = {'sell', 'short'}

        # TODO: can these be duplicates of parents threads, not sure how 4chan works
        # make a list of processes ids
        # scan replies too
        for reply in thread.replies:
            parse_tokens(reply.comment)


def scan_all():
    # grab the first thread on the board by checking first page
    board = basc_py4chan.Board('biz')
    all_thread_ids = board.get_all_thread_ids()

    # newest threads start at 0
    for i in range(len(all_thread_ids)):
    #for i in range(20):
        if i % 10 == 0:
            print('parsing thread ', i, ' / ', len(all_thread_ids))

        read_thread(board, all_thread_ids[i])


def update():
    all_coins = get_json('https://api.coinmarketcap.com/v1/ticker/')

    # TODO: we will need a special dict, because we want to keep coin on btc and bitcoin, etc.
    # TODO: do we want to keep case sensitive counts? (more confidence when symbol is upper case for known words)

    for coin in all_coins:
        symbol = coin['symbol'].lower()

        counts[symbol] = {
            'symbol': symbol,
            'basic': 0,
            'sentiment': 0,
            'buysell': 0
        }

    scan_all()

    sorted_counts = sorted(counts.values(), key=lambda item:item['basic'])

    for item in sorted_counts:
        count = item['basic']
        if count > 0:
            print(item['symbol'], ': count = ', count, ', sentiment count = ', item['sentiment'])

if __name__ == '__main__':
    update()