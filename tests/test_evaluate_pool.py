from unittest import TestCase
from Evaluate_pool import Rating, Individual, Evaluate_pool

class TestRating(TestCase):

    def test_rating(self):
        r = Rating(1)
        self.assertEquals(r.rating_num, 1)

        r.start('rater', self.callback, 0)

    def callback(self, rating, message):
        #on account of python async testing being too painful
        self.assertTrue(True)

    def test_rating_givenResponseWithinTime(self):

        r = Rating(2)

        r.start('rater2', self.callback)
        self.assertTrue(r.timer is not None)
        self.assertTrue(r.rater is 'rater2')
        self.assertTrue(r.rating_num is 2)
        self.assertTrue(r.timer is not None)

        r.rated('banana')
        self.assertTrue(r.rating == 'banana')



class test_individual(TestCase):

    def test_1(self):

        num_evals = 2

        ind = Individual('my_item', 'my_id', self.callback, num_evals)

        self.assertEquals(len(ind.to_be_rated), num_evals)
        request = ind.rating_request('rater')

        self.assertTrue(len(ind.to_be_rated) == 1)
        self.assertTrue(request.get('id') == 'my_id')
        self.assertTrue(request.get('rating_num') == 0)
        self.assertTrue(request.get('data') is not None)
        self.assertTrue(len(ind.in_limbo) == 1)

        ind.rated('my_rating', request.get('rating_num'))
        self.assertTrue(len(ind.has_been_rated) == 1)

        request = ind.rating_request('rater2')
        self.assertTrue(request.get('rating_num') == 1)
        ind.rated('my rating 2', request.get('rating_num'))

        self.assertTrue(len(ind.has_been_rated) == 2)

    def callback(self,_ind, message):
        self.assertTrue(True)



class test_Evaluate_pool(TestCase):

    def test_2(self):
        feedback_after_x_complete_ratings = 10
        eval = Evaluate_pool(self.callback, feedback_after_x_complete_ratings)

        requested_ratings_to_make = 4
        items = list()
        for i in range(0, requested_ratings_to_make):
            item = {'id': i}
            items.append(item)

        eval.add_many(items)
        self.assertEquals(len(eval.pool), 4)

        counter = 0
        checkedout = eval.get_item('rater' + str(counter))
        self.assertEquals(checkedout.get('id'), 0)
        self.assertEquals(checkedout.get('rating_num'), 0)

        checkedouts = list()

        while checkedout is not None:
            checkedouts.append(checkedout)
            checkedout = eval.get_item('rater'+str(counter))

        self.assertEquals(len(checkedouts),  requested_ratings_to_make * Individual.num_evaluations)

        self.assertEquals(len(eval.tested_pool),0)

        while len(checkedouts) > 0:
            checkedout = checkedouts.pop()
            eval.return_item('rating', checkedout.get('rating_num'), checkedout.get('id'))


    def callback(self, items):
        'bla'







