from django.shortcuts import render,redirect
from django.db.models import Avg
from utils.utils import project_is_reported ,comment_is_reported
from .models import Project, Report, Picture, Tag, Donation,Rate,Comment
from categories.models import Category
import math
import json


from datetime import datetime
from django.http import HttpResponse
# import os
# from app.forms import Image/

# from werkzeug.utils import secure_filename

# @app.route("projects/launch_project.html", methods=["POST"])

def index(req):
    projects = project_is_reported(Project.objects.all())
    context = {
        'projects':projects
    }
    return render(req, 'projects/index.html', context)

def launch_project(request):
    if request.method.lower() == "get":
        categories= Category.objects.filter()
        context={"categories":categories} 
        return render(request,"projects/launch_project.html",context)
    elif request.method.lower() =="post":
        title = request.POST["title"]
        # category = request.FILES.get("category")
        category = request.POST["category"]
        print (category)

        details = request.POST["details"]
        target = request.POST["target"]
        current = request.POST["current"]
        # featured = request.POST["featured"]
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        # pictures = request.FILES.getlist("picture[]",None)
        # picture=request.FILES.get('picture', None)
        cat=Category.objects.get(pk=category)
        print (cat)
        project_instance=Project.objects.create(featured=0,end_date=end_date,start_date=start_date,
        title=title,details=details,target=target,current=current
        ,category=cat
        )
        for picture in request.FILES.getlist("picture[]",None):
            if picture is not None and picture != '':
                picture_instance=Picture.objects.create(picture=picture,project=project_instance)
        
        searchForValue = ','
        tag = request.POST["tag"]
        if tag is not None and tag != '':
            if searchForValue in tag:
                tags=tag.split(',')
                for tag in tags:
                    tag_instance=Tag.objects.create(tag=tag,project=project_instance)       
            else:    
                tag_instance=Tag.objects.create(tag=tag,project=project_instance)
        

        projects= Project.objects.filter()
        categories= Category.objects.filter()
        context={"projects":projects,"categories":categories} 
        return render(request,"projects/launch_project.html",context)



def admin_projects(request):
    projects = Project.objects.all()

    return render(request, 'projects/admin/all.html', {'projects':projects})

def admin_delete_projects(request, id):
    project = Project.objects.get(pk=id)
    project.delete()
    return redirect('/admin/projects/')


def show(req,project_id):
    user_id=1 #will be replaced by logged user
    project_data  = Project.objects.get(id=project_id)
    pictures_data = Picture.objects.filter(project_id=project_id)
    is_reported=Report.objects.filter(project_id=project_id,user_id=1);
    comments = comment_is_reported(Comment.objects.filter(project_id=project_id))
    tags=project_data.tag_set.filter(project_id=project_id).values('tag')
    project_ids=Tag.objects.filter(tag__in=tags).exclude(project_id =project_id).values('project_id')
    print(project_ids)
    projects = Project.objects.filter(id__in=project_ids)[0:5]
    try:
        user_rate = Rate.objects.get(project_id=project_id,user_id=1)
        user_rate_val=f"you rated this project { user_rate }"
    except Rate.DoesNotExist:
        user_rate = None
        user_rate_val=f"you haven't rated this project yet"


    avg_rating_dict=Rate.objects.filter(project_id=project_id).aggregate(Avg('rate'))
    if avg_rating_dict['rate__avg']:
        avg_rating= math.floor(float(avg_rating_dict['rate__avg'])*10)/10
    else:
        avg_rating=0



    context={
        'projects' : projects,
        'project'  : project_data,
        'time'     :  project_data.end_date.date() < datetime.now().date(),
        'pictures'  : pictures_data,
        'reported' : is_reported,
        'comments' : comments,
        'user_rate_val': user_rate_val,
        'rating'   : avg_rating ,
        'rating_f' : int( ( avg_rating-int(avg_rating) )*10 ),
        'rating_i' : range(int(avg_rating)),
        }
    return render(req, 'projects/show.html', context)

def comment(req):
    user_id=1
    new_comment=Comment(
                comment=req.POST['comment'],
                project_id=req.POST['project_id'],
                user_id=1
                )
    new_comment.save()            
    return redirect(f"/projects/{req.POST['project_id'] }" )            



def rate(req,project_id):
    try:
        rate_exists = Rate.objects.get(project_id=project_id,user_id=1)
    except Rate.DoesNotExist:
        rate_exists = None
    if rate_exists:
        rate_exists.rate=req.GET['rate_val']
        rate_exists.save()
        response_message=["Rate has been updated"]
    else:
        new_rate = Rate(project_id=project_id,user_id=1,rate=req.GET['rate_val'])
        new_rate.save()
    return redirect(f"/projects/{project_id}" )  

