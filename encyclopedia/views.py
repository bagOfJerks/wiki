from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
import re
from . import util
from random import randint

#syntax:
#title is the name of the entry, which appears in the first header (if author does it that way) and is the file name
#entry refers to the file itself
#body refers to the text inside the entry

#this list is displayed as UL in new and edit pages as a simple guide to markdown.
#TODO: make more interactive so it displays it? how to do that without hard-coding in HTML page?
markdownHints = [
    "# header: (display as big header)",
    "## 2nd header: (display as 2nd biggest header) (and so on up to six header levels)",
    "[Python](/wiki/Python): (dispaly a link to page called 'Python')",
    "To put a new paragraph, use two returns, but don't use tabs or spaces!",
    "to put in a line break, use two spaces then Return",
    "make text **bold** or __bold__",
    "make text *italic*",
    "block quote by putting > at start of paragraph"
]

#form definitions for new and editing entries
class NewEntryForm(forms.Form):
    newEntryTitle = forms.CharField(label="title:")
    newEntryBody = forms.CharField(label="", widget=forms.Textarea(attrs={'cols': 5, 'rows': 3}))

class EditEntryForm(forms.Form):
    editEntryBody = forms.CharField(label="edit entry here:", widget=forms.Textarea(attrs={'cols': 5, 'rows': 3}))

def newEntry(request):
    #when you post to new entry, it creates the entry
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid(): 
            newEntryTitle = form.cleaned_data["newEntryTitle"]
            #check if entry already exists. if so give error message, TODO: provide link to edit
            #TODO: can this be done in real time in the form with a popup?
            if newEntryTitle in util.list_entries():
                return message(request, "an entry of that name is existant. to edit?")
            else:
                #if not in list, save as new entry
                #append title to front of body with appropriate markdown fomatting, so entry automatically is formatted corectly
                newEntryBody = form.cleaned_data["newEntryBody"]
                util.save_entry(newEntryTitle, bytes(newEntryBody, 'utf8'))
                #sends you to wiki article for that page
                return wiki(request, newEntryTitle)
        else:
            #if not succesful, display an error message
            #this would only happen if form is not valid, but at the moment I'm not sure when this would happen
            return message(request, "message", "To sorry but an error is occurant.")
    #when you go to new entry with GET, you get the new entry form
    if request.method == "GET":
        #make a NewEntryForm called form, and send as_p so form is rendered as paragraphs
        form = NewEntryForm()
        return render(request, "encyclopedia/newEntry.html",{
            "form": form.as_p(),
            "markdownHints": markdownHints
        })

def edit(request, title):
#takes you to edit page (like new page) but fills out form with existing entry
#TODO: can this be integrated into a single form with new entry? maybe just lock title input box, and have some logic as to whether this is "new" or "edit"?
    #retrieve existing article body to populate the form
    entry = util.get_entry(title)
    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid(): 
            editedEntryBody = form.cleaned_data["editEntryBody"]
            #need to add bytes(..., 'utf8') to entry to avoid doubling new lines when saving
            #relates to using a windows vs. unix machine? per this forum answer: https://stackoverflow.com/questions/63004501/newlines-in-textarea-are-doubled-in-number-when-saved
            util.save_entry(title, bytes(editedEntryBody, 'utf8'))
            #sends you to wiki article for the edited page
            return wiki(request, title)
        else:
            #if not succesful, redirect you back to new entry page. TODO: give an error message of some kind?
            return render(request, "encyclopedia/edit.html",{
                "form": EditEntryForm(initial={'editEntryBody': entry}),
                "title": title
            })
    #when you go to new entry with GET, you get the new entry form
    #pass entry text as initial so it's already in the window
    if request.method == "GET":
        return render(request, "encyclopedia/edit.html",{
            "form": EditEntryForm(initial={'editEntryBody': entry}),
            "title": title,
            "markdownHints": markdownHints
        })

def index(request):
    #TODO: how can you make the search work for all pages? i.e. if you're on a wiki page, it won't work right now.
    #get query term if any was input into search form - this is syntax that I found on a forum
    #https://stackoverflow.com/questions/53920004/add-q-searchterm-in-django-url
    q = request.GET.get('q')
    #if there is no q value, then brings up index page with list of all entries
    if q is None:
        return render(request, "encyclopedia/index.html", {
            "title": "All Pages",
            "entries": util.list_entries()
        })
    #if there is a value for q, then perform a search
    else:
        #define RegEx that's just the search term input, ignore case
        searchRegex = re.compile(q, re.I)
        #make a list of all entries
        entries = util.list_entries()
        #make an empty list that will hold entry titles of all matches
        searchResults = []
        #loop over every entry. if there's a match, add entry title to search results
        for entry in entries:
            #search entry, save results as list (search result)
            searchResult = searchRegex.search(entry)
            #if there is a result, searchResult will be a list. if there's no match, searchResult is empty. We don't do anything with the results themselves, we just want to know if there's a hit.
            if searchResult != None:
                searchResults.append(entry)
        #if there is exactly one item in searchResults, redirect to that wiki page
        if len(searchResults) == 1:
            #return wiki(request, searchResults[0])
            title = searchResults[0]
            return HttpResponseRedirect("wiki/%s" %title)
        #if there is > 1 item in searchResults, display list of results
        elif len(searchResults) > 1:
            #return message(request, searchResults)
            return render(request, "encyclopedia/index.html", {
                "title": ("Search Results for %s" %q),
                "entries": searchResults
            })
        #if there's zero results, display message saying no results
        else:
            return message(request, "was not to match any entries. To make one?")

# this will take you to entry called "title" when you go to wiki/title
def wiki(request, title):
    #if entry does not exist, return message. TODO: put a link to create an article with that name?
    if util.get_entry(title) is None:
        return message(request, "there is no entry of that name! To create one?")
    else:
        #if entry does exist, reutrn wiki.html, passing the title and article as inputs to be displayed
        return render(request, "encyclopedia/wiki.html", {
            "title" : title,
            "body" : util.get_entry(title)
        })

#direct you to a random entry's wiki page
def random(request):
    #generate list of all entries
    entries = util.list_entries()
    #pick entry from list with random number between zero and length of list - 1
    randomEntry = entries[randint(0, len(entries)-1)]
    #display entry based on number
    return HttpResponseRedirect("wiki/%s" %randomEntry)

#this is check code - delete later. static url for testing if a link works
#before adding dynamic URL
def testpage(request):
    return render(request, "encyclopedia/testpage.html")

#this brings you to a blank warrning page that displays a message.
#called from other functions when you want to return a message.
#TODO: can we pass this page html links? for example, if search turns up no results, put a link to maket the page?
def message(request, message):
    return render(request, "encyclopedia/message.html",{
        "message": message
    })