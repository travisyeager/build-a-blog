import webapp2, jinja2, os, re
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

def get_posts(self, limit, offset):
    q = Post.all().order('-created')
    return q.fetch(limit=limit, offset=offset)

class Blog(webapp2.RequestHandler):
    page_size = 5
    get_posts = get_posts
    def get(self):
        page = self.request.get("page")
        offset = 0
        page = page and int(page)
        if page:
            offset = (int(page) - 1) * self.page_size
        else:
            page = 1
        if page > 1:
            prev_page = page - 1
        else:
            prev_page = None
        posts = self.get_posts(self.page_size, offset)
        if len(posts) == self.page_size and Post.all().count() > offset+self.page_size:
            next_page = page + 1
        else:
            next_page = None
        t = jinja_env.get_template("blog.html")
        response = t.render(posts=posts, page=page, page_size=self.page_size, prev_page=prev_page, next_page=next_page)
        self.response.out.write(response)

class NewPost(webapp2.RequestHandler):
    def render_form(self, title="", body="", error=""):
        t = jinja_env.get_template("newpost.html")
        response = t.render(title=title, body=body, error=error)
        self.response.out.write(response)
    def get(self):
        self.render_form()
    def post(self):
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
            error = id + " doesn't exist"
            t = jinja_env.get_template("404.html")
            response = t.render(error=error)
        self.response.out.write(response)

app = webapp2.WSGIApplication([
    ('/', Blog),
    ('/newpost', NewPost),
    webapp2.Route('/<id:\d+>', ViewPostHandler),
], debug=True)
