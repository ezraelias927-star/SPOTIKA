from flask import Flask,render_template,redirect,url_for,request,session
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__)
app.secret_key="hhdjjfifgiururuuu7476578686tnfgdye7ee6y3y3n"
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import event
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///mimi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
from datetime import datetime
    

class mechi(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    timuA=db.Column(db.String(50),nullable=False)
    timuB=db.Column(db.String(50),nullable=False)
    aina=db.Column(db.String(50),nullable=False)
    odds=db.Column(db.Integer,nullable=False)
    status=db.Column(db.String(50))
    special=db.Column(db.String(50))
    tarehe=db.Column(db.String(50))


@event.listens_for(mechi.odds,'set')
def autofill(target,value,oldvalue,initiator):
    if value>=2:
        target.status="good odds"
    else:
       target.status="bad odds"

    at=db.relationship('mechia',backref='mec',uselist=False)
    bt=db.relationship('mechib',backref='mechi',uselist=False)

class register(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),nullable=False,unique=True)
    password=db.Column(db.String(50),nullable=False,unique=True)
    email=db.Column(db.String(50),nullable=False,unique=True)


class mechia(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    magoli=db.Column(db.Integer,nullable=False)
    corner=db.Column(db.Integer,nullable=False)
    fomu=db.Column(db.Integer,nullable=False)
    fk=db.Column(db.Integer,db.ForeignKey('mechi.id'))


class mechib(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    magoli=db.Column(db.Integer,nullable=False)
    corner=db.Column(db.Integer,nullable=False)
    fomu=db.Column(db.Integer,nullable=False)
    fk=db.Column(db.Integer,db.ForeignKey('mechi.id'))

#HAPA NI SEHEMU YA KUJASILI WATUMIAJI
@app.route('/register',methods=['POST','GET'])
def registe():
    if request.method=='POST':
      try:
        username=request.form.get('username')
        password=request.form.get('password')
        hashed=generate_password_hash(password)
        email=request.form.get('email')
        info=register(username=username,password=hashed,email=email)
        db.session.add(info)
        db.session.commit()
        return redirect(url_for('home'))
      except:
          return redirect(url_for('registe'))
    return render_template('register.html')


#FANYA LOGIN
@app.route('/login', methods=["POST","GET"])
def login():
    if request.method=="POST":
      try:
        username=request.form.get('username')
        password=request.form.get('password')
        cred=register.query.filter_by(username=username).first()
        if username and username=="admin":
            return redirect(url_for('adminhome'))
        if username and check_password_hash(cred.password,password):
            session['id']=cred.id
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
      except:
          return redirect(url_for('login'))
    return render_template('login.html')



#SELECT ILI KUONESHA MECHI ZOTE TIPS
@app.route('/')
def home():
    leo=datetime.now()
    format=leo.strftime("%Y-%m-%d")
    hom=mechi.query.filter_by(tarehe=format)
    jumla=1
    for t in hom:
        jumla*=t.odds
    return render_template('home.html',hom=hom,jumla=jumla)


#KUANDIKA MECHI ZILIZOPO
@app.route('/andika',methods=['POST','GET'])
def andika():
    if request.method=='POST':
     try:
      timuA=request.form.get('timuA')
      timuB=request.form.get('timuB')
      aina=request.form.get('aina')
      odds=float(request.form.get('odds'))
      special=request.form.get('special')
      tarehe=request.form.get('tarehe')
      wote=mechi(timuA=timuA,timuB=timuB,aina=aina,odds=odds,special=special,tarehe=tarehe)
      db.session.add(wote)
      db.session.commit()
      return redirect(url_for('adminhome'))
     except:
         return "andika values"
    return render_template('adminjaza.html')

@app.route('/nyumbani')
def each():
    leo=datetime.now()
    format=leo.strftime("%Y-%m-%d")
    matokeo=mechi.query.filter_by(tarehe=format).all()
    return render_template( 'matokeo.html',matokeo=matokeo)

#KUJAZA TAARIFA ZA KILA MECHI
@app.route('/teamA/<int:id>',methods=['POST','GET'])
def teamA(id):
    if request.method=='POST':
        try:
         magoli=int(request.form.get('magoli'))
         corner=int(request.form.get('corner'))
         fomu=int(request.form.get('fomu'))
         kisha=mechia(magoli=magoli,corner=corner,fomu=fomu,fk=id)
         db.session.add(kisha)
         db.session.commit()
         return redirect(url_for('adminhome'))
        except:
            return 'umekosea'
    user=mechi.query.get(id)
    return render_template('ente.html',user=user)

#KUANGALIA AINA ZA MECHI OPTION
@app.route('/anga/<aina>')
def anga(aina):
   try:
    leo=datetime.now()
    format=leo.strftime("%Y-%m-%d")
    matokeo=mechi.query.filter_by(aina=aina,tarehe=format)
    jumla=1
    for t in matokeo:
        jumla*=t.odds
    return render_template('aina.html',matokeo=matokeo,jumla=jumla)
   except:
      return redirect(url_for('joins'))

#INITIATE ID FOR GENERATING AINA
@app.route('/joins')
def joins():
   try:
    matokeo=mechi.query.with_entities(mechi.aina).distinct().all()
    return render_template('xaxa.html',matokeo=matokeo)
   except:
      return redirect(url_for('joins'))

@app.route('/okay')
def okay():
    oka=db.session.query(mechi).join(mechia).filter(mechia.magoli==1).all()
    return render_template('oka.html',oka=oka)

#ADMIN HOME
@app.route('/adminhome')
def adminhome():
    return render_template('adminhome.html')

#ADMIN FETCH ALL USERS
@app.route('/adminuser')
def adminuser():
    zote=mechi.query.all()
    return render_template('adminzote.html',zote=zote)

#UPDATE MATCHES
@app.route('/update/<int:id>',methods=['POST','GET'])
def adminupdate(id):
    mat=mechi.query.get(id)
    timuA=request.form.get('timuA')
    timuB=request.form.get('timuB')
    aina=request.form.get('aina')
    odds=float(request.form.get('odds'))
    special=request.form.get('special')
    tarehe=request.form.get('tarehe')
    mat.timuA=timuA
    mat.timuB=timuB
    mat.aina=aina
    mat.odds=odds
    mat.special=special
    mat.tarehe=tarehe
    db.session.commit()
    return redirect(url_for('adminuser'))

#KUDELETE MECHI
@app.route('/delete/<int:id>')
def delete(id):
    mat=mechi.query.get(id)
    db.session.delete(mat)
    db.session.commit()
    return redirect(url_for('adminuser'))

#KUANGALIA SPECIAL TIPS ZA LEO
@app.route('/spec')
def spec():
    matokeo=mechi.query.filter_by(tarehe=format,special='special')
    jumla=1
    for t in matokeo:
        jumla*=t.odds
    return render_template('special.html',matokeo=matokeo, jumla=jumla)

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
