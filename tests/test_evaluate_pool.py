from unittest import TestCase
from EvaluationManager import Rating, Individual, EvaluationManager
from random import random

class TestRating(TestCase):

    def test_rating(self):
        params = {'time_out': 1}
        r = Rating(1, params)
        self.assertEquals(r.rating_num, 1 )

        r.start('rater', self.callback)

    def callback(self):
        #on account of python async testing being too painful
        self.assertTrue(True)

    def test_rating_givenResponseWithinTime(self):
        params = {'time_out': 1}
        r = Rating(2, params)

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
        default_num_evaluations = 5

        params = {'num_evals': num_evals, 'num_evals': 5}
        ind = Individual('my_item', 'my_id', self.callback, params)

        self.assertEquals(len(ind.to_be_rated), default_num_evaluations)
        request = ind.rating_request('rater')

        self.assertTrue(len(ind.to_be_rated) == 4)
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

    def test_failed_assessment(self):
        params = {'num_evals': 2, 'num_evals': 5}
        ind = Individual('my_item', 'my_id', self.callback, params)

        self.assertEquals(len(ind.to_be_rated),5)
        rating_request = ind.rating_request('rater')

        failed_rating = ind.in_limbo[0]
        self.assertEquals(len(ind.to_be_rated), 4)
        failed_rating.do_callback()
        self.assertEquals(len(ind.to_be_rated), 5)

    def callback(self):
        self.assertTrue(True)



class TestEvaluatePool(TestCase):

    def test_2(self):

        callback_self = self

        def callback(_items):

            callback_self.assertEquals(len(_items), 3)
            callback_self.assertEquals(len(eval.pool), 0)

            #there is 1 item left over in potentially_tested_pool as this function is not async - code still running
            callback_self.assertEquals(len(eval.potentially_tested_pool), 1)


        params = {'minimum_finished': 3, "num_evals":5}
        eval = EvaluationManager(callback, params)

        items_to_evaluate = 4
        items = list()
        for i in range(0, items_to_evaluate):
            item = {'id': i}
            items.append(item)

        eval.add_many(items)

        self.assertEquals(len(eval.pool), items_to_evaluate)

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

        # is 20
        self.assertEquals(len(checkedouts), items_to_evaluate * params.get('num_evals'))

        self.assertEquals(len(eval.tested_pool),0)

        dict = {}
        for i in range(0,items_to_evaluate):
            dict[i] = 0

        for checkedout in checkedouts:
            dict[checkedout.get('id')] += 1

        for key in dict.keys():
            self.assertEquals(dict.get(key), params.get('num_evals'))


        for checkedout in checkedouts:
            rating_num = checkedout.get('rating_num')
            _id = checkedout.get('id')
            eval.return_item('rating', rating_num, _id)
            with self.assertRaises(ValueError):
                #when tried to return a second time, should raise an error
                eval.return_item('rating', rating_num, _id)


        #after everything done, should be 1 item remaining in finished_pool
        self.assertEquals(len(eval.tested_pool), 1)
        left_over = eval.tested_pool[0]
        self.assertEquals(left_over.id, 3)
        self.assertEquals(len(left_over.in_limbo), 0)
        self.assertEquals(len(left_over.has_been_rated), params.get('num_evals'))


class TestEvalWithRandData(TestCase):

    def test1(self):

        items_to_evaluate = 50
        minimum_finished = items_to_evaluate + 1  # we dont want this to ever occur
        num_eval = 5

        eval = EvaluationManager(None, {'minimum_finished': minimum_finished, 'num_evals': num_eval})

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

        #test to see that data tallies
        for i in range(0, len(items)):

            item__data = items[i].get('test_data')
            derived_item__data = results[i].data

            for i_rating in range(0,num_eval):
                self.assertEquals(item__data[i_rating], derived_item__data[i_rating])





