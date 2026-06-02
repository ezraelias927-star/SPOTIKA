from flask import Flask,render_template,redirect,url_for,request,session,flash,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
import requests
app=Flask(__name__)
app.secret_key="hhdjjfifgiururuuu7476578686tnfgdye7ee6y3y3n"
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import event
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///mimi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
from datetime import datetime,timedelta
from dotenv import load_dotenv
load_dotenv()
import os
app.secret_key=os.getenv('APPKEY')
    

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
    password=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(50),nullable=False)


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
          flash('username ipo tayari! andika username nyingine!')
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
        if cred and cred.username=="admin":
            if cred and check_password_hash(cred.password,password):
              return redirect(url_for('andika'))
        if cred and check_password_hash(cred.password,password):
            session['id']=cred.id
            return redirect(url_for('home'))
        else:
            flash('umeingiza taarifa zisizo sahihi! jaribu tena!!')
            return redirect(url_for('login'))
      except:
          return redirect(url_for('home'))
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
      return redirect(url_for('andika'))
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

#kwenda vip
@app.route('/tospecial')
def tospecial():
   return render_template('tospecial.html')

#kuanzisha malipo
@app.route('/vip')
def vip():
    url="https://cybqa.pesapal.com/pesapalv3/api/Auth/RequestToken"
    KEY=os.getenv('KEY')
    SECRET=os.getenv('SECRET')
    payload={
        'consumer_key':KEY,
        'consumer_secret':SECRET
    }
    headers={
        'Accept':'application/json',
        'Content-Type':'application/json'
    }
    response=requests.post(url=url,json=payload,headers=headers)
    data=response.json()
    token=data.get('token')
    print(data)
    
    #kupata ipn kwa sasa
    ipn_id=os.getenv('IPN_ID')
    # 1. Endpoint ya kutengeneza Order/Invoice
    submit_order_url = "https://cybqa.pesapal.com/pesapalv3/api/Transactions/SubmitOrderRequest"
    
    # Headers zinabaki vile vile zikiwa na Bearer Token wetu
    headers_order = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    print('hello')
    
    # 2. Payload ya Muamala (Hapa ndio unaweka data za hela sasa)

    leo=datetime.now()
    formatted=leo.strftime('%Y%m%d%H%M%S%f')
    
    payload_order = {
        "id":formatted,                 
        "currency": "TZS",                  
        "amount": 10000.00,                  
        "description": "Malipo ya Huduma",     
        "callback_url": "https://spotika.dig.co.tz/payment-callback", 
        "notification_id": ipn_id,            
        "billing_address": {
            "email_address": "ezra@gmail.com",
            "phone_number": "0712345678",
            "first_name": "Ezra",
            "last_name": "Developer"
        }
    }  


    
    # 3. Kupiga API ya Pesapal kuomba hiyo link
    response_order = requests.post(url=submit_order_url, json=payload_order, headers=headers_order)
    data_order = response_order.json()
    redirect_url=data_order['redirect_url']
    print(data_order)
    return redirect(redirect_url)

#kupata callback url
@app.route('/payment-callback')
def callback():
   return 'sdfghjkgfdfghjkgfdfghjkjhgfdfgj'

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
      flash('machaguo hayapo! yatawekwa hivi punde!!')
      return redirect(url_for('joins'))

#Kuonesha aina ya machaguo
@app.route('/joins')
def joins():
    matokeo=mechi.query.with_entities(mechi.aina).distinct().all()
    return render_template('xaxa.html',matokeo=matokeo)


@app.route('/okay')
def okay():
    oka=db.session.query(mechi).join(mechia).filter(mechia.magoli==1).all()
    return render_template('oka.html',oka=oka)

#kuchuja mechi kulingana na tarehe(jana,leo na kesho)
@app.route('/filter')
def filter():
   tarehe=datetime.now()
   formatted=tarehe.strftime('%Y-%m-%d')

#kuchuja mechi za jana
@app.route('/jana')
def jana():
   leo=datetime.now()
   jana=leo-timedelta(days=1)
   formatted=jana.strftime("%Y-%m-%d")
   mec=mechi.query.filter_by(tarehe=formatted)
   for m in mec:
       data={
          'timuA':m.timuA,
          'timuB':m.timuB,
          'aina':m.aina,
          'odds':m.odds,
          'status':m.special,
          'status':m.tarehe,
         }
       list.append(data)
       print(f'list ni {len(list)}........')
       return jsonify(list)
   return render_template('both.html',mec=mec)

   return render_template('both.html',mec=mec)

#kuonesha mechi za kesho
@app.route('/kesho')
def kesho():
   leo=datetime.now()
   jana=leo+timedelta(days=1)
   formatted=jana.strftime("%Y-%m-%d")
   mec=mechi.query.filter_by(tarehe=formatted)
   if mec:
    list=[]
    for m in mec:
       data={
          'timuA':m.timuA,
          'timuB':m.timuB,
          'aina':m.aina,
          'odds':m.odds,
          'status':m.special,
          'status':m.tarehe,
         }
       list.append(data)
   print(f'list ni {list}........')
   return jsonify(list)

#kuonesha mechi za leo
print('......hapa ni leo')
@app.route('/leo')
def leo():
   leo=datetime.now()
   formatted=leo.strftime("%Y-%m-%d")
   mec=mechi.query.filter_by(tarehe=formatted).all()
   print(f'........mechi ni {len(mec)}......')
   list=[]
   for m in mec:
       data={
          'timuA':m.timuA,
          'timuB':m.timuB,
          'aina':m.aina,
          'odds':m.odds,
          'status':m.special,
          'tarehe':m.tarehe,
        }
       list.append(data)
   print(f'data ni {list}........')
   return jsonify(list)

#kuonesha remplates ya mechi yenye mechi tayri
@app.route('/mec')
def mec(): 
   return render_template('both.html')

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
@app.route('/update/<int:id>',methods=['POST'])
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
   try:
    leo=datetime.now()
    format=leo.strftime("%Y-%m-%d")
    matokeo=mechi.query.filter_by(tarehe=format,special='special')
    jumla=1
    for t in matokeo:
        jumla*=t.odds
    return render_template('special.html',matokeo=matokeo, jumla=jumla)
   except:
      return redirect(url_for('home'))
   
#KUSELECT USERS WOTE FOR DISPLAY
@app.route('/users')
def users():
   matokeo=register.query.all()
   return render_template('adminusers.html',matokeo=matokeo)

#KUUPDATE USERS WALIOPO
@app.route('/adminupdates/<int:id>',methods=['POST'])
def adminupdates(id):
   matokeo=register.query.get(id)
   username=request.form.get('username')
   password=request.form.get('password')
   email=request.form.get('email')
   matokeo.username=username
   matokeo.password=password
   matokeo.email=email
   db.session.commit()
   return redirect(url_for('users'))

#KUDELETE USERS
@app.route('/deleteusers/<int:id>')
def deleteusers(id):
   matokeo=register.query.get(id)
   db.session.delete(matokeo)
   db.session.commit()
   return redirect(url_for('users'))




if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
