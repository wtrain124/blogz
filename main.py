from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app= Flask(__name__)
app.config['DEBUG'] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key= '#someSecretString'

class Blog(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      title = db.Column(db.String(120))
      body = db.Column(db.Text)
      owner_id= db.Column(db.Integer, db.ForeignKey('user.id'))
      created= db.Column(db.DateTime)

      def __init__(self,title,body,owner):
            self.title = title
            self.body = body
            self.owner= owner 
            self.created= datetime.utcnow()

class User(db.Model):
      id= db.Column(db.Integer,primary_key= True)
      username = db.Column(db.String(120), unique=True)
      password = db.Column(db.String(120))
      blogs = db.relationship('Blog', backref= 'owner') 

      def __init__(self, username, password):
            self.username= username
            self.password= password

def username_valid(username):
      if '@' in username:
            return False
      if len(username)<= 1:
            return False
      if username==' ':
            return False
      
      return True


@app.before_request
def require_login():
      allowed_routes= ['login', 'blog','index','signup']
      if request.endpoint not in allowed_routes and 'username' not in session:
            return redirect('/login')

@app.route('/', methods = ['POST','GET'])
def index():

      users= User.query.all()
      return render_template("/index.html",users=users)

@app.route('/signup', methods = ['POST','GET'])
def signup():
      if request.method =='POST':
            username= request.form['username']
            password= request.form['password']
            verify= request.form['verify']
            #session['username'] = username

            existing_user= User.query.filter_by(username=username).first()
            if not existing_user:
                  #todo - validate user's data
                  username_good= username_valid(username)
                  pass_good= password ==verify and len(password) > 4
                        
                  if username_good and not pass_good:
                        session['username'] = username
                        if password != verify:
                              flash("Password does not match", "error")
                        else:
                              flash("Invalid password","error")      
                        return redirect('/signup')

                  if username_good and pass_good:
                        new_user= User(username,password)
                        flash("Logged in", "success")

                        db.session.add(new_user)
                        db.session.commit()
                        session['username'] = username
                        return redirect('/newpost')

                  if not username_good:
                        flash("Invalid username","error")
                        return redirect('/signup')
                  if not pass_good:
                        flash("Invalid password","error")
                        return redirect('/signup')

            if existing_user:
                  flash("Username already exists","error")
                  return redirect('/signup')

      return render_template('signup.html')

@app.route('/login', methods = ['POST','GET'])
def login():
      if request.method == 'POST':
            username= request.form['username']
            password= request.form['password']
            user= User.query.filter_by(username=username).first()
   
            if user and user.password == password:
                  session['username'] = username
                  flash("Logged in", "success")
                  return redirect('/newpost')
            elif user and user.password != password:
                  session['username'] = username
                  flash("Incorrect password", "error")
                  return redirect('/login')
            else:
                  flash('User does not exist', 'error')
                  return redirect('/login')

      return render_template('login.html')

@app.route('/logout', methods = ['POST','GET'])
def logout():
      del session['username']
      return redirect("/blog")



@app.route('/blog', methods = ['POST','GET'])
def blog():
      if "user" in request.args:
            user_id = request.args.get("user")
            user = User.query.get(user_id)
            user_blogs = Blog.query.filter_by(owner=user).all()
            return render_template("singleUser.html", title = user.username + "'s blogs", 
                  user_blogs=user_blogs) 

      blog_id= request.args.get("id")

      if (blog_id)== None:
            blogs= Blog.query.all()
            return render_template("blog.html", title= "List of Blog Entries", blogs= blogs)

      else:
            blog= Blog.query.get(blog_id)
            return render_template("single.html", title="Whoa look at that!", blog=blog)


#TODO: Consider what needs to happen here with the new parameter added.
#TODO: Might need to consider the username and password being correct.
@app.route('/newpost', methods = ['POST','GET'])
def newpost():
      owner = User.query.filter_by(username= session['username']).first()

      if request.method == 'POST':
            title = request.form['title']
            body= request.form['body']
            new_blog = Blog(owner=owner,title=title,body=body)

            db.session.add(new_blog)
            db.session.commit() 

            url= "/blog?id=" + str(new_blog.id)
        
            return redirect(url)
      else:
            return render_template('newpost.html')




if __name__ == '__main__':
      app.run()