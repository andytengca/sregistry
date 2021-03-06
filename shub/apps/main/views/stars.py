'''

Copyright (C) 2017-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from shub.apps.main.models import (
    Container, 
    Collection,
    Star
)

from django.shortcuts import (
    get_object_or_404, 
    render_to_response, 
    render, 
    redirect
)

from django.db.models.aggregates import Count
from django.http import (
    JsonResponse, 
    HttpResponseRedirect
)
from .collections import get_collection
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages


import os
import re
import uuid


###############################################################################################
# COLLECTIONS #################################################################################
###############################################################################################

def collection_stars(request):
    '''This is a "favorite" view of collections ordered based on number of stars.
    '''
   
    # Favorites based on stars
    collections = Collection.objects.filter(private=False).annotate(Count('star', distinct=True)).order_by('-star__count')
    collections = [x for x in collections if x.star__count>0]
    context = {"collections": collections }
    return render(request, 'stars/collection_stars.html', context)


def collection_downloads(request):
    '''This is a "favorite" view of collections ordered based on number of downloads.
    '''

    from shub.apps.logs.models import APIRequestCount
    favorites = APIRequestCount.objects.filter(method="get",path__contains="ContainerDetailByName").order_by('-count')

    context = {"favorites": favorites }
    return render(request, 'stars/collection_downloads.html', context)


#######################################################################################
# COLLECTION STARS
#######################################################################################

@login_required
def star_collection(request,cid):
    '''change favorite status of collection. If it's favorited, unfavorite by deleting
    the star. If not, then create it.
    '''
    collection = get_collection(cid)
    try:
        star = Star.objects.get(user=request.user,
                                collection=collection)
    except:
        star = None

    if star is None:
        star = Star.objects.create(user=request.user,
                                   collection=collection)
        star.save()
        status = {'status':'added'}
    else:
        star.delete()
        status = {'status':'removed'}

    return JsonResponse(status)
