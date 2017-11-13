# -*- coding: utf-8 -*-

from django.shortcuts import render,HttpResponse
from django.contrib.auth.decorators import login_required
from usercenter.permissions import check_permission
import json
from kingadmin.admin_base import site
from django.core.paginator import Paginator


@login_required()
def index(request):
    enabled_admins = site.enabled_admins
    return render(request,"base/index.html",locals())


def test(request):
    all_obj = [
        {
            "id": 1,
            "name": "name1",
            "users": "users1",
            "comment": "comment1",
        },
        {
            "id": 2,
            "name": "name2",
            "users": "users1",
            "comment": "comment1",
        },
        {
            "id": 3,
            "name": "name3",
            "users": "users1",
            "comment": "comment1",
        },
        {
            "id": 4,
            "name": "name4",
            "users": "users1",
            "comment": "comment1",
        },
        {
            "id": 5,
            "name": "name5",
            "users": "users1",
            "comment": "comment1",
        },
        {
            "id": 6,
            "name": "name6",
            "users": "users1",
            "comment": "comment1",
        },
        {
            "id": 7,
            "name": "name7",
            "users": "users1",
            "comment": "comment1",
        },
        {
            "id": 8,
            "name": "name8",
            "users": "users1",
            "comment": "comment1",
        },
        {
            "id": 9,
            "name": "name9",
            "users": "users1",
            "comment": "comment1",
        }
    ]
    if request.method == 'GET':
        # user_all = User.objects.all()
        user_all = [
            {
                "id":1,
                "name": "name1",
                "users": "users1",
                "comment": "comment1",
            }
        ]
        print request.GET
        # return render('test.html', locals(), request)
    else:
        print request.POST
        page_length = int(request.POST.get('length', '5'))
        total_length = len(all_obj)
        keyword = request.POST.get(u'search')
        print '---'+keyword+'----'
        rest = {
            "iTotalRecords": page_length,  # 本次加载记录数量
            "iTotalDisplayRecords": total_length,  # 总记录数量
            "aaData": []}
        page_start = int(request.POST.get('start', '0'))
        page_end = page_start + page_length
        page_data = all_obj[page_start:page_end]
        data = []
        for item in page_data:
            res = {}
            res['id'] = item['id']
            res['name'] = item['name']
            res['users'] = 5
            res['comment'] = item['comment']
            data.append(res)
        rest['aaData'] = data
        return HttpResponse(json.dumps(rest), content_type='application/json')

    return render(request,'test.html', locals())



