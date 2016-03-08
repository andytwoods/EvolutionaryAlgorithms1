from unittest import TestCase
from Evaluate_pool import Rating, Individual, Evaluate_pool
from random import random

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



class TestIndividual(TestCase):

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


class TestEvaluatePool(TestCase):

    def test_2(self):
        feedback_after_x_complete_item_ratings = 3

        callback_self = self

        def callback(items):
            callback_self.assertEquals(len(items), 3)
            callback_self.assertEquals(len(eval.pool), 0)
            #there is 1 item left over in potentially_tested_pool as this function is not async - code still running
            callback_self.assertEquals(len(eval.potentially_tested_pool), 1)

        eval = Evaluate_pool(callback, feedback_after_x_complete_item_ratings)

        items_to_evaluate = 4
        items = list()
        for i in range(0, items_to_evaluate):
            item = {'id': i}
            items.append(item)

        eval.add_many(items)
        self.assertEquals(len(eval.pool), 4)

        counter = 0
        checkedout = eval.get_item('rater' + str(counter))
        self.assertEquals(checkedout.get('id'), 0)
        self.assertEquals(checkedout.get('rating_num'), 0)

        checkedouts = list()

        #this gets all possible ratings to undertake
        while checkedout is not None:
            counter += 1
            checkedouts.append(checkedout)
            checkedout = eval.get_item('rater'+str(counter))

        self.assertEquals(len(checkedouts), items_to_evaluate * Individual.default_num_evaluations)

        self.assertEquals(len(eval.tested_pool),0)

        dict = {}
        for i in range(0,items_to_evaluate):
            dict[i] = 0

        for checkedout in checkedouts:
            dict[checkedout.get('id')] += 1

        for key in dict.keys():
            self.assertEquals(dict.get(key), Individual.default_num_evaluations)


        for checkedout in checkedouts:
            eval.return_item('rating', checkedout.get('rating_num'), checkedout.get('id'))
            with self.assertRaises(ValueError):
                #when tried to return a second time, should raise an error
                eval.return_item('rating', checkedout.get('rating_num'), checkedout.get('id'))

        #after everything done, should be 1 item remaining in finished_pool
        self.assertEquals(len(eval.tested_pool),1)
        left_over = eval.tested_pool[0]
        self.assertEquals(left_over.id, 3)
        self.assertEquals(len(left_over.in_limbo), 0)
        self.assertEquals(len(left_over.has_been_rated), Individual.default_num_evaluations)


class TestEvalWithRandData(TestCase):

    def test1(self):

        items_to_evaluate = 50
        feedback_after_x_complete_item_ratings = items_to_evaluate+1 #we dont want this to ever occur
        num_eval = 5

        eval = Evaluate_pool(None, feedback_after_x_complete_item_ratings, num_eval)

        def test_data():
            mock = []
            for i in range(0, num_eval):
                mock.append(random())
            return mock

        #generate items and for each random data
        items = list()
        for i in range(0, items_to_evaluate):
            item = {'id': i, 'test_data': test_data()}
            items.append(item)

        eval.add_many(items)

        checkedouts = list()
        counter = 0
        checkedout = eval.get_item('rater' + str(counter))

        #this gets all possible ratings to undertake
        while checkedout is not None:
            counter += 1
            checkedouts.append(checkedout)
            checkedout = eval.get_item('rater'+str(counter))



        self.assertEquals(len(checkedouts), items_to_evaluate * num_eval)
        print "-------------------------------"
        for i in range(0, len(items)):
            item = items[i]
            for eval_num in range(0, num_eval):
                checkedout = checkedouts.pop(0)
                eval.return_item(item.get('test_data')[eval_num], checkedout.get('rating_num'), checkedout.get('id'))

        self.assertEquals(len(eval.pool), 0)
        self.assertEquals(len(eval.potentially_tested_pool), 0)

        results = eval.tested_pool

        for i in range(0, len(items)):

            item__data = items[i].get('test_data')
            derived_item__data = results[i].data

            for i_rating in range(0,num_eval):
                self.assertEquals(item__data[i_rating], derived_item__data[i_rating])





