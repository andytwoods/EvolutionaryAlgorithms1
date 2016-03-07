import threading


class Evaluate_pool(object):
    def __init__(self, callback, minimum_finished):
        self.callback = callback
        self.pool = list()
        self.minimum_finished = minimum_finished
        self.potentially_tested_pool = list()
        self.tested_pool = list()
        self.id_counter = 0

    def add(self, item):
        self.pool.append(Individual(item, self.id_counter, self._callback_individual))
        self.id_counter += 1

    def add_many(self, items):
        for item in items:
            self.add(item)

    def _callback_individual(self, individual, message):
        if message == "data collected":
            self.potentially_tested_pool.remove(individual)
            self.tested_pool.append(individual)
            if len(self.tested_pool) >= self.minimum_finished:
                test_these = list()
                for tested in self.tested_pool:
                    self.tested_pool.remove(tested)
                    test_these.append(tested)
                    self.callback(test_these)

    def get_item(self, rater):

        if len(self.pool)==0: return None


        item = self.pool[0]
        info = item.rating_request(rater)

        if item.potentially_finished is True:
            self.pool.remove(item)
            self.potentially_tested_pool.append(item)

        return info

    def return_item(self, rating, rating_num, id):
        for item in self.pool:
            if item.id == id:
                item.rated(rating, rating_num)
                return

        raise ValueError('the item was not found in the pool. Devel error.')


class Individual(object):
    num_evaluations = 5

    def __init__(self, item, individual_id, callback, evals=-1):
        self.item = item
        self.id = individual_id
        self.callback = callback
        self.to_be_rated = []
        self.has_been_rated = []
        self.in_limbo = []
        self.potentially_finished = False
        if evals is -1:
            self.num_evaluations = self.num_evaluations
        else:
            self.num_evaluations = evals

        self.new_rating(self.num_evaluations)

    def rating_request(self, rater):

        rating = self.to_be_rated.pop(0)
        rating.start(rater, self.callback_rating, False)
        self.in_limbo.insert(0, rating)

        if len(self.to_be_rated) == 0:
            self.potentially_finished = True

        return {'id': self.id, 'rating_num': rating.rating_num, 'data': 'self.item'}

    def new_rating(self, how_many):
        for i in range(0, how_many):
            rating_num = len(self.to_be_rated)
            self.to_be_rated.append(Rating(rating_num))

    def callback_rating(self, rating, action):
        if action == 'late':
            self.new_rating(1)

    def rated(self, rating, rating_num):

        for rating in self.in_limbo:
            if rating.rating_num == rating_num:
                rating.rated(rating)
                self.in_limbo.remove(rating)
                self.has_been_rated.insert(0, rating)
                if len(self.has_been_rated) == self.num_evaluations:
                    self.finished = True
                    self.callback(self, 'data collected')
                return

        raise ValueError('When returning a rating, the rating number was not found. Devel error.')


class Rating(object):
    timeout = 60

    def __init__(self, rating_num):
        self.rating = None
        self.rater = None
        self.timer = None
        self.callback = None
        self.rating_num = rating_num

    def start(self, rater, callback, force_timeout=False):
        self.rater = rater

        self.callback = callback
        self.timer = threading.Timer(Rating.timeout, self.do_callback)

        if force_timeout is True:
            self.timer.cancel()
            self.do_callback()

    def do_callback(self):
        self.callback(self, 'late')

    def rated(self, rating):
        self.stop_timeout()
        self.rating = rating

    def stop_timeout(self):
        self.timer.cancel()
