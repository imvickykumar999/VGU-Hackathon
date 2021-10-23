
from datetime import datetime
from bson.json_util import dumps
from flask_socketio import SocketIO
from pymongo.errors import DuplicateKeyError
import requests, os
from bs4 import BeautifulSoup as bs
from werkzeug.utils import secure_filename
from flask import Flask, flash, jsonify, url_for, session, request, redirect, render_template, send_from_directory
from flask_qrcode import QRcode
from PIL import Image
import ast, json, urllib.request as ur

UPLOAD_FOLDER = 'uploads'
try:
    os.mkdir('uploads')
except Exception as e:
    print(e)
    pass

try:
    os.mkdir('uploads/audio')
except Exception as e:
    print(e)
    pass

try:
    os.mkdir('uploads/news')
except Exception as e:
    print(e)
    pass

app = Flask(__name__)
app.secret_key = "secret key"

socketio = SocketIO(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def callviews():
    from vicks import crud
    obj1 = crud.vicks('@Hey_Vicks', link = 'https://home-automation-336c0-default-rtdb.firebaseio.com/')
    pageviews = obj1.pull(child = 'Views')
    pageviews += 1
    obj1.push(data = pageviews, child = 'Views')
    return pageviews

# pageviews = callviews()

# ======================================================

@app.route("/maps")
def maps():

    import re
    import json
    from urllib.request import urlopen

    url = 'http://ipinfo.io/json'
    response = urlopen(url)
    data = json.load(response)

    site_json = {'alt': {},
                 'elevation': {},
                 'latt': '27.17312',
                 'longt': '78.04137',
                 'standard': {'addresst': 'Taj Mahal Internal Path',
                              'city': 'Agra',
                              'confidence': '0.7',
                              'countryname': 'India',
                              'latt': '27.17312',
                              'longt': '78.04137',
                              'postal': '282006',
                              'prov': 'IN',
                              'region': 'Uttar Pradesh',
                              'stnumber': '1'}}

    tablejson = site_json['standard']

    return render_template('maps.html',
                            check='no error',
                            site_json = site_json,
                            tablejson = tablejson,
                            data=data,
                            scroll='vickscroll',
                        )


@app.route("/vicks_maps", methods=['POST', 'GET'])
def vicks_maps():

    try:
        import re
        import json
        from urllib.request import urlopen

        url = 'http://ipinfo.io/json'
        response = urlopen(url)
        data = json.load(response)

        from urllib import request
        from flask import request as req
        from bs4 import BeautifulSoup
        import json

        from pprint import pprint as p
        from urllib.parse import quote

        loc = req.form['maps']
        text_encoded = quote(loc)
        url = f'https://geocode.xyz/{text_encoded}?json=1'

        html = request.urlopen(url).read()
        soup = BeautifulSoup(html,'html.parser')

        site_json = json.loads(soup.text)
        check = list(site_json.keys())[0]
        print('-------------->', check)

        try:
            tablejson = site_json['standard']
        except:
            tablejson = site_json

        return render_template('maps.html',
                               scroll='vickscroll',
                               site_json=site_json,
                               data=data,
                               tablejson=tablejson,
                               check=check,
                               )
    except:
        site_json = {'alt': {},
                     'elevation': {},
                     'latt': '27.17312',
                     'longt': '78.04137',
                     'standard': {'addresst': 'Taj Mahal Internal Path',
                                  'city': 'Agra',
                                  'confidence': '0.7',
                                  'countryname': 'India',
                                  'latt': '27.17312',
                                  'longt': '78.04137',
                                  'postal': '282006',
                                  'prov': 'IN',
                                  'region': 'Uttar Pradesh',
                                  'stnumber': '1'}}

        tablejson = site_json['standard']

        return render_template('maps.html',
                                check='no error',
                                data=data,
                                site_json = site_json,
                                tablejson = tablejson,
                                scroll='vickscroll',
                            )

# -------------------------------------------------

@app.route('/uploads/audio/<filename>')
def send_audio(filename):
    return send_from_directory("uploads/audio", filename)

# ========================================================

@app.route("/vicksmail")
def vicksmail():
    return render_template("mailsent.html", sent='no')

@app.route("/mail_sent", methods=['POST'])
def mail_sent():
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "sagar.sws2000@gmail.com"
    toaddr = request.form['user']

    if request.form['pass'] == '@Hey_Vicks' and toaddr in ['imvickykumar999@gmail.com', 'ankitmalpani1975@gmail.com']:
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr

        msg['Subject'] = "Vicks OTP"
        import random
        otp = str(random.randint(1000,9999))

        file1 = open("otp.txt", "w")
        file1.write(otp)
        file1.write(toaddr)
        file1.close()

        body = f'''\
            <html>
              <head>Vicks Quotes</head>
              <body>

                <h2 style="color:green;">
                   Hi, <br> {''.join(toaddr.split('@')[0])}
                </h2>
                <br>

               <h1>
                   Here is the OTP you wanted.
                   <br><br> {otp}
               </h1>

                 <br>
                 <a target="_blank" href="https://imvickykumar999.herokuapp.com/admin">
                   <h3 style="color:red;">
                     <strong>
                       Redirect to Vicks Quote.
                     </strong>
                   </h3>
                 </a>

              </body>
            </html>
        '''
        msg.attach(MIMEText(body, 'html'))

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, "vguhackathon")

        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()
        return render_template("mailsent.html", sent='yes')
    else:
        return render_template("404.html", message = 'Unauthenticated Email ID or Password')

@app.route("/admin")
def admin():
    # https://console.firebase.google.com/u/0/project/chatting-c937e/database/chatting-c937e-default-rtdb/data
    from vicks import crud
    obj1 = crud.vicks('@Hey_Vicks', link = 'https://home-automation-336c0-default-rtdb.firebaseio.com/')

    data = obj1.pull('Group/Chat')
    # print('=============================', data)

    if data == None:
        obj1.push()

    data = obj1.pull('Group/Chat')
    print('------------------------->', data)
    pageviews = callviews()
    return render_template("admin.html",
                           # scroll='vickscroll',
                           pageviews=pageviews,
                           data = data,
                           )

@app.route('/<filename>')
def send_aadhar(filename):
    return send_from_directory(".", filename)

@app.route('/converted_admin', methods=['POST'])
def converted_admin():
    from vicks import crud
    credentials = '@Hey_Vicks'

    turn = request.form['turn']
    f = request.files['file']
    aadhar = request.form['aadhar'] + '.' + f.filename.split('.')[1]

    f.save(secure_filename(aadhar))
    otp = request.form['otp'].strip()

    f=open("otp.txt",'r')
    f = f.read()
    getotp = f[:4]
    person = f[4:].split('@')[0]

    f = open("otp.txt", "w")
    f.write('-')
    f.close()

    if otp == getotp and otp != '-':
        obj1 = crud.vicks(credentials, name = [turn, aadhar.split('.')[0], person], link = 'https://home-automation-336c0-default-rtdb.firebaseio.com/')
        obj1.push(data = 1, child = 'A/B/C/Switch')

        message = f'''
        {request.form['message']}
        Description : {request.form['description']}
        '''
        if message == '':
            obj1.push()
        else:
            obj1.push(message)

        from gtts import gTTS
        tts = gTTS(message)
        tts.save(f"uploads/crime/{aadhar.split('.')[0]}.mp3")

        data = obj1.pull('Group/Chat')
        print('------------------------->', data)
        pageviews = callviews()
        print('====//////////---->>>', aadhar)

        return render_template("user.html",
                               # scroll='vickscroll',
                               pageviews=pageviews,
                               data = data,
                               )
    else:
        return render_template("404.html", message = 'Wrong OTP')

# ====================================================

@app.route('/')
def user():
    from vicks import crud
    obj1 = crud.vicks('@Hey_Vicks', link = 'https://home-automation-336c0-default-rtdb.firebaseio.com/')

    data = obj1.pull('Group/Chat')
    if data == None:
        obj1.push()

    data = obj1.pull('Group/Chat')
    print('------------------------->', data)
    pageviews = callviews()
    return render_template("user.html",
                           # scroll='vickscroll',
                           pageviews=pageviews,
                           data = data,
                           )

# --------------------------------------------

@app.route('/uploads/<filename>')
def send_image(filename):
    return send_from_directory("uploads", filename)

# =============================================

@app.route('/news')
def news():
    from gtts import gTTS
    try:
        pageviews = callviews()
        print('= = = = = = = => ', pageviews)

        link = 'https://inshorts.com/en/read'
        req = requests.get(link)

        soup = bs(req.content, 'html5lib')
        box = soup.findAll('div', attrs = {'class':'news-card z-depth-1'})

        ha,ia,ba,la,ta,sa = [],[],[],[],[],[]
        for i in range(len(box)):
            h = box[i].find('span', attrs = {'itemprop':'headline'}).text

            m = box[i].find('div', attrs = {'class':'news-card-image'})
            m = m['style'].split("'")[1]

            s = box[i].find('div', attrs = {'class':'news-card-title news-right-box'}).a['href']
            s = 'https://inshorts.com' + s

            b = box[i].find('div', attrs = {'itemprop':'articleBody'}).text
            tts = gTTS(b)
            t = ''.join([i for i in h if i.isalpha()])

            l='link not found'
            try:
                l = box[i].find('a', attrs = {'class':'source'})['href']
            except:
                pass

            ha.append(h)
            ia.append(m)
            ba.append(b)
            la.append(l)
            ta.append(t)
            sa.append(s)

        return render_template('news.html',
                                ha=ha,
                                ia=ia,
                                ba=ba,
                                la=la,
                                ta=ta,
                                sa=sa,
                                listen=0,
                                pageviews=pageviews,
                                range_ha = range(len(box)),
                                )
    except Exception as e:
        print(e)
        return render_template('404.html')


@app.route('/listen_news', methods=['POST'])
def listen_news():
    from gtts import gTTS

    try:
        listen = request.form['customRadio']
        print('======================>', listen)

        link = 'https://inshorts.com/en/read'
        req = requests.get(link)

        soup = bs(req.content, 'html5lib')
        box = soup.findAll('div', attrs = {'class':'news-card z-depth-1'})

        ha,ia,ba,la,ta,sa = [],[],[],[],[],[]
        if listen == '0':
            range_ha = len(box)
        else:
            range_ha = 10

        for i in range(range_ha):
            h = box[i].find('span', attrs = {'itemprop':'headline'}).text

            m = box[i].find('div', attrs = {'class':'news-card-image'})
            m = m['style'].split("'")[1]

            s = box[i].find('div', attrs = {'class':'news-card-title news-right-box'}).a['href']
            s = 'https://inshorts.com' + s

            b = box[i].find('div', attrs = {'itemprop':'articleBody'}).text
            tts = gTTS(b)

            t = ''.join([i for i in h if i.isalpha()])

            # if empty:
            if listen == '1':
                tts.save(f'uploads/news/{t}.mp3')

            l='link not found'
            try:
                l = box[i].find('a', attrs = {'class':'source'})['href']
            except:
                pass

            ha.append(h)
            ia.append(m)
            ba.append(b)
            la.append(l)
            ta.append(t)
            sa.append(s)

        return render_template('news.html',
                                ha=ha,
                                ia=ia,
                                ba=ba,
                                la=la,
                                sa=sa,
                                ta=ta,
                                listen=listen,
                                scroll='vickscroll',
                                range_ha = range(range_ha),
                                )
    except Exception as e:
        print(e)
        return render_template('404.html')

# ==========================================================

@app.route('/uploads/news/<filename>')
def send_news(filename):
    return send_from_directory("uploads/news", filename)

@app.route('/uploads/crime/<filename>')
def send_crime(filename):
    return send_from_directory("uploads/crime", filename)

# ==================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message = 'Try Again Later...'), 404

if __name__ == '__main__':
    socketio.run(app, debug=True)
