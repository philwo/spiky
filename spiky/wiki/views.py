# -*- coding: utf-8 -*-

# Spiky views
from __future__ import with_statement

from spiky.wiki.models import *

from django import newforms as forms
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from difflib import HtmlDiff, SequenceMatcher
from datetime import date, timedelta
import os
from subprocess import Popen, PIPE

from pygments import highlight
from pygments.lexer import RegexLexer
import pygments.token
from pygments.formatters import HtmlFormatter


### FORM SPECIFICATIONS ###

###### FORM FOR USER SIGN-UP ######
class SignupForm(forms.Form):
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileForm(forms.Form):
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()


###### FORM FOR SEARCHING PAGES ######
class SearchForm(forms.Form):
    text = forms.CharField(label="Enter your search query")
    search_titles = forms.BooleanField(label="Search titles?", required=False, initial=True)
    search_content = forms.BooleanField(label="Search content?", required=False)
    search_tags = forms.BooleanField(label="Search tags?", required=False)


### PUBLIC VIEWS ###

###### SIGN-UP FOR AN ACCOUNT ######
def signup(request):
    if request.method == "POST":
        r = SignupForm(request.POST)
        if not r.is_valid():
            return render_to_response(settings.TEMPLATE_DIR + "signup.html", {
                "signupform": r,
                "base_site": settings.BASE_SITE,
                "content": "Error"
            }, context_instance=RequestContext(request))
        else:

            user = User.objects.create_user(
                username=r.cleaned_data["username"],
                email=r.cleaned_data["email"],
                password=r.cleaned_data["password"])
            user.first_name = r.cleaned_data["first_name"]
            user.last_name = r.cleaned_data["last_name"]
            user.save()

            return HttpResponseRedirect("/accounts/login/")

    r = SignupForm()
    return render_to_response(settings.TEMPLATE_DIR + "signup.html", {
        "signupform": r,
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### LIST ALL PAGES ######
def list_pages(request):
    pages = Page.objects.currentpages()
    users = User.objects.order_by("username")
    return render_to_response(settings.TEMPLATE_DIR + "list.html", {
        "page_name": "ListPage",
        "pages": pages,
        "users": users,
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### SEARCH ######
def search_pages(request):
    if request.method == "POST":
        f = SearchForm(request.POST)
        if not f.is_valid():
            return render_to_response(settings.TEMPLATE_DIR + "search.html", {
                "form": f,
                "content": "no results",
                "base_site": settings.BASE_SITE
            }, context_instance=RequestContext(request))
        else:
            pages = Page.objects.currentpages()

            matches_title = []
            if f.cleaned_data["search_titles"]:
                matches_title = pages.filter(name__icontains=f.cleaned_data["text"])

            matches_contents = []
            if f.cleaned_data["search_content"]:
                matches_contents = pages.filter(content__icontains=f.cleaned_data["text"])

            matches_tags = []
            if f.cleaned_data["search_tags"]:
                matches_tags = pages.filter(tags__name__icontains=f.cleaned_data["text"])

            return render_to_response(settings.TEMPLATE_DIR + "search.html", {
                "form": f,
                "matches_title": matches_title,
                "matches_contents": matches_contents,
                "matches_tags": matches_tags,
                "base_site": settings.BASE_SITE
            }, context_instance=RequestContext(request))

    f = SearchForm()
    return render_to_response(settings.TEMPLATE_DIR + "search.html", {
        "page_name": "SearchPage",
        "form": f,
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### LIST ALL TAGS ######
def list_tags(request):
    return render_to_response(settings.TEMPLATE_DIR + "tags.html", {
        "page_name": "TagCloud",
        "tags": Tag.objects.all(),
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### VIEW A SPECIFIC TAG ######
def view_tag(request, tag_name):
    return render_to_response(settings.TEMPLATE_DIR + "tag.html", {
        "page_name": "Tag: " + tag_name,
        "pages": Page.objects.currentpages().filter(tags__name__exact=tag_name),
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### START PAGE ######
def start(request):
    return HttpResponseRedirect("/Start/")


###### VIEW A PAGE ######
def view_page(request, page_name, rev=None):
    if rev == None:
        page = Page.objects.filter(name=page_name).order_by("-rev")[:1]

        if len(page) == 0:
            return render_to_response(settings.TEMPLATE_DIR + "create.html", {
                "page_name": page_name,
                "base_site": settings.BASE_SITE
            }, context_instance=RequestContext(request))

        oldrev = False
        page = page[0]
    else:
        oldrev = True
        page = get_object_or_404(Page, rev=rev)

    return render_to_response(settings.TEMPLATE_DIR + "view.html", {
        "uid": page.uid,
        "rev": page.rev,
        "page_name": page.name,
        "oldrev": oldrev,
        "content": Page.wiki2html(page.wikisyntax, page.content),
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### VIEW A PAGE (GET BY UID) ######
def view_page_by_uid(request, uid):
    page = Page.objects.filter(uid=uid).order_by("-rev")[:1]
    if len(page) == 0:
        raise Http404
    page = page[0]
    return view_page(request, page.name)


###### UTILITY FUNCTION: GET LAST DAY OF MONTH ######
def get_last_day_of_month(year, month):
    if (month == 12):
        year += 1
        month = 1
    else:
        month += 1
    return date(year, month, 1) - timedelta(1)


###### VIEW THE CALENDAR ######
def view_calendar(request, year=date.today().year, month=date.today().month):
    year = int(year)
    month = int(month)
    first_day_of_month = date(year, month, 1)
    last_day_of_month = get_last_day_of_month(year, month)
    first_day_of_calendar = first_day_of_month - timedelta(first_day_of_month.weekday())
    last_day_of_calendar = last_day_of_month + timedelta(7 - last_day_of_month.weekday())

    pages = Page.objects.order_by("last_modified")

    month_cal = []
    week = []
    week_headers = []

    if month == 1:
        prevmonth = "/spiky/calendar/%d/%d/" % (year - 1, 12)
        nextmonth = "/spiky/calendar/%d/%d/" % (year, month + 1)
    elif month == 12:
        prevmonth = "/spiky/calendar/%d/%d/" % (year, month)
        nextmonth = "/spiky/calendar/%d/%d/" % (year + 1, 1)
    else:
        prevmonth = "/spiky/calendar/%d/%d/" % (year, month - 1)
        nextmonth = "/spiky/calendar/%d/%d/" % (year, month + 1)

    i = 0
    day = first_day_of_calendar
    while day <= last_day_of_calendar:
        if i < 7:
            week_headers.append(day)
        cal_day = {}
        cal_day["day"] = day
        cal_day["event"] = False
        cal_day["pages"] = []

        for page in pages:
            if day == page.last_modified.date():
                cal_day["event"] = True
                page.modify_count = 1
                if len(cal_day["pages"]) >= 1:
                    prevpage = cal_day["pages"][-1:][0]
                    if prevpage.uid == page.uid and prevpage.last_modified_by == page.last_modified_by:
                        prevpage.last_modified_end = page.last_modified
                        prevpage.modify_count += 1
                    else:
                        cal_day["pages"].append(page)
                else:
                    cal_day["pages"].append(page)
        if day.month == month:
            cal_day["in_month"] = True
        else:
            cal_day["in_month"] = False
        week.append(cal_day)
        if day.weekday() == 6:
            month_cal.append(week)
            week = []
        i += 1
        day += timedelta(1)

    return render_to_response(settings.TEMPLATE_DIR + "calendar.html", {
        "page_name": "Calendar",
        "calendar": month_cal,
        "headers": week_headers,
        "prevmonth": prevmonth,
        "nextmonth": nextmonth,
        "current": "%s / %s" % (year, month),
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### VIEW THE LOG OF A PAGE ######
def show_log(request, page_name):
    page = Page.objects.filter(name=page_name).order_by("-rev")[:1]

    if len(page) == 0:
        raise Http404

    revisions = Page.objects.filter(uid=page[0].uid).order_by("rev")

    predecessor = None
    for rev in revisions:
        rev.predecessor = predecessor
        predecessor = rev

    return render_to_response(settings.TEMPLATE_DIR + "log.html", {
        "page_name": page[0].name,
        "newestrev": page[0].rev,
        "revisions": revisions,
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### COMPARE TWO REVISIONS ######
def compare(request, rev1, rev2):
    page1 = get_object_or_404(Page, rev=rev1)
    page2 = get_object_or_404(Page, rev=rev2)

    # We only compare two pages if they have the same UID!
    if page1.uid != page2.uid:
        raise Http404

    diffengine = HtmlDiff(tabsize=4, wrapcolumn=65)
    htmldiff = diffengine.make_table(fromlines=page1.content.split("\n"),
                                    tolines=page2.content.split("\n"),
                                    fromdesc=page1.name,
                                    todesc=page2.name,
                                    context=False)

    return render_to_response(settings.TEMPLATE_DIR + "compare.html", {
        "page1": page1,
        "page2": page2,
        "htmldiff": htmldiff,
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### STATIC PAGE: CONTACT ######
def contact(request):
    return render_to_response(settings.TEMPLATE_DIR + "contact.html", {
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### STATIC PAGE: IMPRINT ######
def imprint(request):
    return render_to_response(settings.TEMPLATE_DIR + "imprint.html", {
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


### VIEWS REQUIRING A LOGIN ###

###### EDIT USER PROFILE ######
@login_required
def profile(request):
    if request.method == "POST":
        r = ProfileForm(request.POST)
        if not r.is_valid():
            return render_to_response(settings.TEMPLATE_DIR + "profile.html", {
                "profileform": r,
                "base_site": settings.BASE_SITE,
                "content": "Error"
            }, context_instance=RequestContext(request))
        else:
            request.user.username = r.cleaned_data["username"]
            request.user.email = r.cleaned_data["email"]
            request.user.first_name = r.cleaned_data["first_name"]
            request.user.last_name = r.cleaned_data["last_name"]
            request.user.save()

            return render_to_response(settings.TEMPLATE_DIR + "profile.html", {
                "page_name": "Profil",
                "profileform": r,
                "base_site": settings.BASE_SITE,
                "content": "changed"
            }, context_instance=RequestContext(request))

    data = {
        "username": request.user.username,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
    }

    r = ProfileForm(data)
    return render_to_response(settings.TEMPLATE_DIR + "profile.html", {
        "page_name": "Profil",
        "profileform": r,
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### WEBSERVICE: RENDER SOME CONTENT (USED BY LIVE-PREVIEW) ######
@login_required
def preview(request):
    if request.method != "POST":
        raise Http404
    return HttpResponse("<div>" + Page.wiki2html(WikiSyntax.objects.get(pk=request.POST["wikisyntax"]), request.POST["content"]) + "</div>")


###### WEBSERVICE: DIFF TWO REVISIONS ######
@login_required
def diff(request, v1, v2):
    from django.utils import simplejson

    page1 = get_object_or_404(Page, rev=v1)
    page2 = get_object_or_404(Page, rev=v2)

    baseText = page1.content
    newText = page2.content

    baseTextName = "Base Text"
    newTextName = "New Text"

    opcodes = SequenceMatcher(None, baseText, newText).get_opcodes()

    resp = HttpResponse()
    resp.write(simplejson.dumps(dict(baseTextLines=baseText, newTextLines=newText, opcodes=opcodes, baseTextName=baseTextName, newTextName=newTextName)))

    return resp


###### WORKFLOW: EDIT A PAGE ######
@login_required
def edit_page(request, page_name):
    page = Page.objects.filter(name=page_name).order_by("-rev")[:1]

    if len(page) == 0:
        # Wir erstellen hier ein neues Page-Objekt, speichern es aber nicht! (Das macht save_page)
        page = Page(uid="",
                    name=page_name,
                    content="",
                    wikisyntax=WikiSyntax.objects.get(pk="creole"),
                    last_modified_by=request.user)
    else:
        page = page[0]

    return render_to_response(settings.TEMPLATE_DIR + "edit.html", {
        "uid": page.uid,
        "rev": page.rev,
        "page_name": page.name,
        "content": page.content,
        "wikisyntax": page.wikisyntax,
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### WORKFLOW: RESTORE OLDER REVISION OF PAGE ######
@login_required
def restore_page(request, page_name, rev):
    old_page = get_object_or_404(Page, rev=rev)

    page = Page(uid=old_page.uid,
                name=old_page.name,
                content=old_page.content,
                storage_type="full",
                wikisyntax=old_page.wikisyntax,
                last_modified_by=request.user)
    page.save()

    return HttpResponseRedirect("/%s/" % (page_name,))


###### WORKFLOW: DELETE A PAGE INCLUDING ALL EARLIER REVISIONS ######
@login_required
def delete_page(request, page_name):
    page = Page.objects.filter(name=page_name).order_by("-rev")[:1]
    if len(page) == 0:
        raise Http404
    page = page[0]
    Page.objects.filter(uid=page.uid).delete()

    return HttpResponseRedirect("/spiky/Start/")


###### WORKFLOW: SAVE AN EDITED PAGE (CREATES A NEW REV) ######
@login_required
def save_page(request, page_name):
    uid = None

    if 'uid' in request.POST:
        uid = request.POST["uid"]

    if 'rev' in request.POST:
        rev = request.POST["rev"]

    name = page_name
    content = request.POST["content"]
    wikisyntax = request.POST["wikisyntax"]

    # ATTENTION: This is not atomic yet! May break under load!
    if uid == None:
        lastpage = Page.objects.order_by("-uid")[:1]

        if len(lastpage) == 0:
            uid = 1
        else:
            uid = lastpage[0].uid + 1

        # Skip conflict management
        rev = 0
        old_rev = 0
    else:
        page = Page.objects.filter(uid=uid).order_by("-rev")[:1][0]
        old_rev = page.rev
        if page.content == content and page.name == name and page.wikisyntax.name == wikisyntax:
            return HttpResponseRedirect("/" + page_name + "/")

    # <CreatePageObj>
    page = Page(uid=uid,
                name=name,
                content=content,
                storage_type="full",
                wikisyntax=WikiSyntax.objects.get(pk=request.POST["wikisyntax"]),
                last_modified_by=request.user)
    # </CreatePageObj>

    # <SavePageToDB>
    page.save()
    # </SavePageToDB>

    # <Konfliktmanagement>
    if int(rev) != old_rev:
        return HttpResponseRedirect("/merge/%d/%d/%d/" % (int(rev), old_rev, page.rev))
    # </Konfliktmanagement>

    return HttpResponseRedirect("/" + page_name + "/")


###### UTILITY CLASS: WDIFF HIGHLIGHTER ######
class WDiffLexer(RegexLexer):
    name = 'WDiff'
    aliases = ['wdiff']
    filenames = ['*.wdiff']
    flags = re.MULTILINE

    tokens = {
        'root': [
            (r'\{\+.*\+\}', pygments.token.Generic.Inserted),
            (r'\[-.*-\]', pygments.token.Generic.Deleted),
            (r'.+', pygments.token.Text),
        ]
    }


###### WORKFLOW: MERGE TWO REVISIONS INTO ONE ######
@login_required
def merge(request, original, theirs, ours):
    original_page = Page.objects.filter(rev=original)[:1][0]
    theirs_page = Page.objects.filter(rev=theirs)[:1][0]
    ours_page = Page.objects.filter(rev=ours)[:1][0]

    # We can only merge pages who are revisions of the same UID!
    if original_page.uid != theirs_page.uid or theirs_page.uid != ours_page.uid:
        raise Http404

    # Dump the content into tempfiles
    tmporig = os.tmpnam()
    tmpours = os.tmpnam()
    tmptheirs = os.tmpnam()
    try:
        f_orig = open(tmporig, "w")
        f_orig.write(original_page.content.replace("\r\n", "\n").encode("utf8"))
        f_orig.flush()
        f_ours = open(tmpours, "w")
        f_ours.write(ours_page.content.replace("\r\n", "\n").encode("utf8"))
        f_ours.flush()
        f_theirs = open(tmptheirs, "w")
        f_theirs.write(theirs_page.content.replace("\r\n", "\n").encode("utf8"))
        f_theirs.flush()

        # Diff them with "wdiff", highlight the output
        diff_ours = highlight(Popen(["wdiff", "-n", tmporig, tmpours], stdout=PIPE).communicate()[0].decode("utf8"), WDiffLexer(), HtmlFormatter())
        diff_theirs = highlight(Popen(["wdiff", "-n", tmporig, tmptheirs], stdout=PIPE).communicate()[0].decode("utf8"), WDiffLexer(), HtmlFormatter())
    finally:
        # Clean up
        os.remove(tmporig)
        os.remove(tmpours)
        os.remove(tmptheirs)
        f_orig.close()
        f_ours.close()
        f_theirs.close()

    return render_to_response(settings.TEMPLATE_DIR + "merge.html", {
        "uid": original_page.uid,
        "page_name": ours_page.name,
        "rev_original": original,
        "rev_theirs": theirs,
        "rev_ours": ours,
        "content_original": original_page.content,
        "content_theirs": theirs_page.content,
        "content_ours": ours_page.content,
        "diff_ours": diff_ours,
        "diff_theirs": diff_theirs,
        "base_site": settings.BASE_SITE
    }, context_instance=RequestContext(request))


###### WORKFLOW: REBUILD ALL PAGES (IF CACHE IS OUTDATED) ######
@login_required
def compile_all(request):
    for p in Page.objects.currentpages():
        p.compile()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", ""))
