from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app= Flask(__name__)
app.config['DEBUG'] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key= '#someSecretString'

class Blog(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      title = db.Column(db.String(120))
      body = db.Column(db.Text)

      def __init__(self,title,body):
            self.title = title
            self.body = body

class Newpost(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      title = db.Column(db.String(120))
      body = db.Column(db.String(120))

      def __init__(self,title,body):
            self.title = title
            self.body = body
            #self.completed = False          


@app.route('/', methods = ['POST','GET'])
def index():
      return redirect("/blog")

      # if request.method == 'POST':
      #       blog_name = request.form['title']
      #       blog_body = request.form['body']
      #       new_post = Blog(blog_name,blog_body)
      #       db.session.add(new_post)
      #       db.session.commit()

      # blogs = Blog.query.filter_by().all()
      # return render_template('blog.html',title="Build a Blog", blogs=blogs)

@app.route('/blog', methods = ['POST','GET'])
def blog():
      blog_id= request.args.get("id")

      if (blog_id)== None:
            blogs= Blog.query.all()
            return render_template("blog.html", title= "Build a Blog", blogs= blogs)

      else:
            blog= Blog.query.get(blog_id)
            return render_template("single.html", title='Yay its done!', blog=blog)
      # if request.method == 'POST':
      #       blogs= Blog.query.all()

      #       return render_template('blog.html', title="Build a Blog", blogs=blogs)
      # else:
      #       post = Blog.query.get(title,body)
      #       return render_template('confirmation.html', post=post, title= "Yay it's done")


@app.route('/newpost', methods = ['POST','GET'])
def newpost():
      if request.method == 'POST':
            title = request.form['title']
            body= request.form['body']
            new_blog = Blog(title=title,body=body)

            db.session.add(new_blog)
            db.session.commit() 

            url= "/blog?id=" + str(new_blog.id)
        
            return redirect(url)
      else:
            return render_template('newpost.html')




if __name__ == '__main__':
      app.run()