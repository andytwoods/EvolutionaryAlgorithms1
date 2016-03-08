import threading


class Evaluate_pool(object):



    def __init__(self, callback, params):
        self._add_defaults(params)
        self.params = params
        self.callback = callback
        self.pool = list()
        self.potentially_tested_pool = list()
        self.tested_pool = list()
        self.id_counter = 0

    @staticmethod
    def _add_defaults(params):

        def check_add(what, default):
            if params.get(what) is None:
                params[what] = default

        check_add('minimum_finished', 5)
        check_add('num_evals', 5)
        check_add('timeout',60)

    def add(self, item):
        self.pool.append(Individual(item, self.id_counter, self._callback_individual, self.params))
        self.id_counter += 1

    def add_many(self, items):
        for item in items:
            self.add(item)

    def _callback_individual(self, individual):

        self.potentially_tested_pool.remove(individual)
        self.tested_pool.append(individual)

        if len(self.tested_pool) >= self.params.get('minimum_finished'):
            test_these = list()
            while len(self.tested_pool) > 0:
                test_these.append(self.tested_pool.pop(0))
            self.callback(test_these)

    def get_item(self, rater):

        if len(self.pool) is 0:
            return None

        item = self.pool[0]
        info = item.rating_request(rater)

        if item.potentially_finished is True:
            self.pool.remove(item)
            self.potentially_tested_pool.append(item)

        return info

    def return_item(self, rating, rating_num, rating_id):
        for given_pool in [self.pool, self.potentially_tested_pool]:
            for item in given_pool:
                if item.id == rating_id:
                    item.rated(rating, rating_num)
                    return

        raise ValueError('the item was not found in the pool. Devel error.')


class Individual(object):

    def __init__(self, item, individual_id, callback, params):
        self.item = item
        self.id = individual_id
        self.callback = callback
        self.to_be_rated = []
        self.has_been_rated = []
        self.in_limbo = []
        self.potentially_finished = False
        self.data = None
        self.finished = False
        self.params = params

        self.new_rating(self.params.get('num_evals'))

    def rating_request(self, rater):

        rating = self.to_be_rated.pop(0)
        rating.start(rater, self.fail_callback_rating)
        self.in_limbo.insert(0, rating)

        if len(self.to_be_rated) == 0:
            self.potentially_finished = True

        return {'id': self.id, 'rating_num': rating.rating_num, 'data': 'self.item'}

    def new_rating(self, how_many):
        for i in range(0, how_many):
            rating_num = len(self.to_be_rated)
            self.to_be_rated.append(Rating(rating_num, self.params))

    def fail_callback_rating(self):
        self.new_rating(1)

    def rated(self, score, rating_num):

        for rating in self.in_limbo:

            if rating.rating_num == rating_num:
                rating.rated(score)
                self.in_limbo.remove(rating)
                self.has_been_rated.append(rating)

                if len(self.has_been_rated) >= self.params.get('num_evals'):
                    self.finished = True
                    self.data = self.compile_data()
                    self.callback(self) #tell parent that data is collected

                return

        raise ValueError('When returning a rating, the rating number was not found. Devel error.')

    def compile_data(self):
        dat = []
        for rating in self.has_been_rated:
            dat.append(rating.rating)
        return dat

class Rating(object):


    def __init__(self, rating_num, params):
        self.rating_num = rating_num
        self.params = params
        self.rating = None
        self.rater = None
        self.timer = None
        self.fail_callback = None

    def start(self, rater, fail_callback):
        self.rater = rater

        self.fail_callback = fail_callback
        self.timer = threading.Timer(self.params.get('time_out'), self.do_callback)

    def do_callback(self):
        self.fail_callback()

    def rated(self, rating):
        self.stop_timeout()
        self.rating = rating

    def stop_timeout(self):
        self.timer.cancel()
