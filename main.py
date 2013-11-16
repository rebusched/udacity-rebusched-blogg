import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

# Defines the database model
class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

# Base handler class
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	def render_str(self, template, **params):
		t = jinja_environment.get_template(template)
		return t.render(params)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

# The blog
class Blog(Handler):
	def get(self):
		posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
		self.render('index.html', posts = posts)

# Render a single post
class Permalink(Handler):
	def get(self, post_id):
		post = Post.get_by_id(int(post_id))

		if not post:
			self.error(404)
			return

		self.render("index.html", posts = [post])

# Submission form
class NewPost(Handler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		if subject and content:
			post = Post(subject = subject, content = content)
			key = post.put()
			self.redirect("/%d" % key.id())
		else:
			error = "Something went wrong. We need both a subject and content"
			self.render("newpost.html",subject=subject, content=content, error=error)

app = webapp2.WSGIApplication([('/', Blog), ('/newpost', NewPost), ('/(\d+)', Permalink)], debug=True)