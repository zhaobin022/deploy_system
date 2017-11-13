from django.test import TestCase
import random
# Create your tests here.



def fun(l,number):
    hight = len(l)-1
    low = 0



    count =0
    while True:
        count += 1
        mid = (hight + low) / 2
        mid_number = l[mid]
        print mid,low,hight,111
        if low <= hight:
            if mid_number == number:
                return mid
            elif number > mid_number:
                low = mid+1
            else:
                hight = mid-1
        else:
            return None




l = [11,123,222,42423,234234234,23423423554,9999999999999999999]
# random.shuffle(l)
print l
print fun(l,234234234)


