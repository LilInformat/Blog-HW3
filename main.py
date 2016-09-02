import os
import re

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def blog_key(name = 'default'):
    return db.Key.from_path('Blog', name)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        blog = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        text=""
        for post in blog:
            text = text + post.subject
        self.response.headers['Content-Type'] = 'text/plain'
        self.write(text)
        #self.render('blog.html', blog=blog)

class PostHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Blog', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render('post.html', post = post)

class NewPostHandler(Handler):
    def render_newpost(self, template, subject="", content="" ,error=""):
        self.render('newpost.html', subject=subject, content=content, error=error)

    def get(self):
        self.render_newpost('newpost.html')

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        error = ""

        if not subject and  not content:
            error = "You're missing a subject and the content"
        elif not subject:
            error = "You're missing a subject!"
        elif not content:
            error = "You're missing the content!"

        if error:
            self.render_newpost('newpost.html', subject=subject, content=content, error=error)
        else:
            post = Blog(parent=blog_key(), subject=subject, content=content)
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))

app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/blog/newpost', NewPostHandler),
    ('/blog/([0-9]+)', PostHandler)
], debug=True)
