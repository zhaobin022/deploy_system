from django.test import TestCase

# Create your tests here.


class A(object):
    def __init__(self):
        self.l = range(9)


    def fun(self):

        for i in self.l:
            print 'before yield'
            yield i
            print 'after yield'

    def __iter__(self):
        return self.fun()



a = A()


for i in a:
    print 'for '
    print i