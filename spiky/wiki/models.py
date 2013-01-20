# -*- coding: utf-8 -*-

# Spiky data models
from __future__ import with_statement

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string

import re
from os import makedirs
from os.path import exists, realpath


#
# UserProfile model which is an add-on to the default Django user-model
#
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    title = models.CharField(max_length=32, blank=True)
    design = models.CharField(max_length=32, default="default")
    bookmarks = models.ManyToManyField("Page")

    class Admin:
        pass


#
# Each page can have multiple tags. A tag is a kind of label.
#
class Tag(models.Model):
    # The label which sticks to the page :)
    name = models.CharField(max_length="32", primary_key=True)

    # We need these two ones to cache some data for the tagcloud.
    # They get recalculated on each Page.save()
    total_ref = models.IntegerField(blank=True, default=0)
    font_size = models.IntegerField(blank=True, default=0)

    def __unicode__(self):
        return self.name

    def __cmp__(self, other):
        return cmp(self.total_ref, other.total_ref)

    class Admin:
        pass


#
# We support different WikiSyntaxes, you can specify one per page.
#
class WikiSyntax(models.Model):
    name = models.CharField(max_length="32", primary_key=True)
    desc = models.CharField(max_length="32", blank=True)


#
# We need a specific manager for the Page objects, because we
# often need to get a list of current pages, that is: A list of
# all pages where each page in the list is the newest revision of its uid.
#
class PageManager(models.Manager):
    def currentpages(self):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT uid, MAX(rev) as rev FROM wiki_page GROUP BY uid")

        result_list = []
        for row in cursor.fetchall():
            result_list.append(row[1])

        return self.model.objects.filter(rev__in=result_list)


#
# Our WikiPage model.
#
class Page(models.Model):
    # We have a global incrementing revision counter.
    # Every revision maps to exactly one page.
    rev = models.AutoField(primary_key=True)

    # A unique id for managing the pages. Each created page
    # has a unique id, which never changes, even if you change
    # the name of the page later-on.
    uid = models.IntegerField()

    # This is the name of the page
    name = models.CharField(max_length="32")

    # We support multiple different storage modules for each
    # page. At the moment this is only "full", but things like
    # "gzip" or "diff" are thinkable.
    storage_type = models.CharField(max_length="64")

    # The content of the page
    content = models.TextField(blank=True)

    # Associated tags
    tags = models.ManyToManyField(Tag)

    # Which wiki syntax gets used for this page?
    wikisyntax = models.ForeignKey(WikiSyntax)

    # Is this page dynamic, i.e. plz never cache it in a static file kthx.
    dynamic = models.BooleanField(default=False)

    # When was the page modified last (actually a page only gets
    # modified once, because each new modification results in a new
    # revision!)
    last_modified = models.DateTimeField(auto_now=True)

    # Who did it. :)
    last_modified_by = models.ForeignKey(User)

    objects = PageManager()

    #
    # A class-method for transforming wiki-syntax content to HTML
    #
    @staticmethod
    def wiki2html(wikisyntax, content):
        from django.utils.encoding import smart_str, force_unicode

        lines = content.split("\n")
        cleaned_content = []
        looking_for_tags = True
        for l in lines:
            if looking_for_tags and l.startswith("@"):
                continue
            else:
                looking_for_tags = False
                cleaned_content.append(l.rstrip())
        cleaned_content = "\n".join(cleaned_content)

        if wikisyntax.name == "creole":
            from creoleparser.core import Parser
            from creoleparser.dialects import Creole10
            my_dialect = Creole10(wiki_links_base_url=settings.SPIKY_BASEURL + "/")
            my_parser = Parser(dialect=my_dialect)
            return my_parser(cleaned_content)
        elif wikisyntax.name == "textile":
            import textile
            return force_unicode(textile.textile(smart_str(cleaned_content), encoding='utf-8', output='utf-8'))
        elif wikisyntax.name == "markdown":
            import markdown
            return force_unicode(markdown.markdown(smart_str(cleaned_content)))
        elif wikisyntax.name == "restructuredtext":
            from docutils.core import publish_parts
            docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})
            parts = publish_parts(source=smart_str(cleaned_content), writer_name="html4css1", settings_overrides=docutils_settings)
            return force_unicode(parts["fragment"])

        raise Exception("Unsupported Wiki Syntax")

    #
    # Compile a wiki page into static HTML and cache it on disk.
    #
    def compile(self):
        html = render_to_string(settings.TEMPLATE_DIR + "view.html", {
            "uid": self.uid,
            "rev": str(self.rev) + " (STATIC)",
            "page_name": self.name,
            "content": self.wiki2html(self.wikisyntax, self.content),
            "base_site": settings.BASE_SITE
        })
        filepath = realpath(settings.SPIKY_CACHEPATH + "/" + self.name)
        if filepath.startswith(settings.SPIKY_CACHEPATH):
            if not exists(filepath):
                makedirs(filepath)

            with open(filepath + "/text.htm", "w") as f:
                f.write(html.encode("utf-8"))

    #
    # Update the tagcloud specific attributes of the tags
    # Inspired by "A Tag cloud solution in Django" by Coulix:
    # http://www.coulix.net/blog/2006/aug/20/tag-cloud-solution-django/
    #
    def process_tag_cloud(self):
        tag_list = Tag.objects.all()

        # First update the ref-counter of all tags (how many pages link to that tag)
        for tag in tag_list:
            tag.total_ref = tag.page_set.all().count()
            tag.save()

        # You can change these values to change the appearance of the tagcloud.
        nbr_of_buckets = 8
        base_font_size = 11

        # Temp vars
        thresholds = []
        max_tag = max(tag_list)
        min_tag = min(tag_list)
        delta = (float(max_tag.total_ref) - float(min_tag.total_ref)) / (float(nbr_of_buckets))

        # Set a threshold for all buckets
        for i in range(nbr_of_buckets):
            thresh_value = float(min_tag.total_ref) + (i + 1) * delta
            thresholds.append(thresh_value)

        # Set font size for tags (per bucket)
        for tag in tag_list:
            font_set_flag = False
            for bucket in range(nbr_of_buckets):
                if font_set_flag == False:
                    if (tag.total_ref <= thresholds[bucket]):
                        tag.font_size = base_font_size + bucket * 2
                        tag.save()
                        font_set_flag = True

    #
    # Handles saving a page, including all other stuff (compiling, updating tagcloud, etc.)
    #
    def save(self):
        super(Page, self).save()

        # <Metainfos>
        # Note, we update all tags for all pages. Yes, this could and should get optimized.
        Tag.objects.all().delete()
        # Precache regex to split tags
        regexp = re.compile("[;,\s]+")
        for p in Page.objects.currentpages():
            for i in p.content.split("\n"):
                # <CheckIsValidMetaLine>
                if not i.startswith("@"):
                    break
                # </CheckIsValidMetaLine>

                # <Tags>
                if i.startswith("@tags "):
                    for t in regexp.split(i[6:].strip(" \r\n")):
                        # Try to associate with existing tag
                        try:
                            tag = Tag.objects.get(name=t)
                        except Tag.DoesNotExist:
                            # Create a new tag
                            tag = Tag(name=t)
                            tag.save()
                        p.tags.add(tag)
                # </Tags>
        # </Metainfos>

        # Call the Django save() method
        super(Page, self).save()

        # Cache
        self.compile()

        # Update tagcloud
        self.process_tag_cloud()

    class Admin:
        pass
