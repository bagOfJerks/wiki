from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    #when you go to wiki/article, you are taken to that article
    path("wiki/<str:title>", views.wiki, name="wiki"),
    #testpage path is check code - can delete later
    path("testpage", views.testpage, name="testpage"),
    #new entry brings you form to create a new entry
    path("newEntry", views.newEntry, name="newEntry"),
    #when you go to edit/article, you are taken to a page to edit that article
    path("edit/<str:title>", views.edit, name="edit"),
    #brings you to a page that displays a message
    path("message", views.message, name="message"),
    #brings you to a random page
    path("random", views.random, name="random")
]
