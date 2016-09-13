import webapp2, jinja2, os, re
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

def get_posts(self, limit):
    q = Post.all().order('-created')
    return q.fetch(limit=limit)

class Blog(webapp2.RequestHandler):
    page_size = 5
    get_posts = get_posts
    def get(self):
        posts = self.get_posts(self.page_size)
        t = jinja_env.get_template("blog.html")
        response = t.render(posts=posts, page_size=self.page_size)
        self.response.out.write(response)

class NewPost(webapp2.RequestHandler):
    def render_form(self, title="", body="", error=""):
        """ Render the new post form with or without an error, based on parameters """
        t = jinja_env.get_template("newpost.html")
        response = t.render(title=title, body=body, error=error)
        self.response.out.write(response)
    def get(self):
        self.render_form()
    def post(self):
        """ Create a new blog post if possible. Otherwise, return with an error message """
        title = self.request.get("title")
        body = self.request.get("body")
        if title and body:
            post = Post(
                title=title,
                body=body)
            post.put()
            id = post.key().id()
            self.redirect("/%s" % id)
        else:
            error = "something went wrong..."
            self.render_form(title, body, error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Post.get_by_id(int(id))
        if post:
            t = jinja_env.get_template("post.html")
            response = t.render(post=post)
        else:
            error = "there is no post with id %s" % id
            t = jinja_env.get_template("404.html")
            response = t.render(error=error)
        self.response.out.write(response)

app = webapp2.WSGIApplication([
    ('/', Blog),
    ('/newpost', NewPost),
    webapp2.Route('/<id:\d+>', ViewPostHandler),
], debug=True)
