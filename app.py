import firebase_admin, os, time, math
from flask import Flask, request
from datetime import datetime, timedelta
from firebase_admin import credentials, firestore

app = Flask(__name__)


@app.route('/readNote', methods=('GET', 'POST'))
def read():
    if request.method == "POST":
        res = {
            "version": "2.0",
            "resultCode": "OK",
            "output": {},
        }
        params = request.get_json()
        sbj = params["action"]["parameters"]["subject"]["value"]
        if sbj == '한능검' or sbj == '한국사':
            query_ref = db.collection('NoteTaking').document('Subjects').collection('History').where('uid', '==', USER_TOKEN).get()
        elif sbj == '컴활':
            query_ref = db.collection('NoteTaking').document('Subjects').collection('CS').where('uid', '==', USER_TOKEN).get()
        elif sbj == '토익':
            query_ref = db.collection('NoteTaking').document('Subjects').collection('Toeic').where('uid', '==', USER_TOKEN).get()
        else:
            res["resultCode"] = "error_unsupported_subject"
            return res
        
        if query_ref:
            txt = ""
            for query in query_ref:
                txt += f"{query.to_dict()['title']}!\n"
                txt += f"{query.to_dict()['contents']}.\n"
        else:
            res["resultCode"] = "error_not_found"
            return res

        res["output"]["contents"] = txt
        return res


@app.route('/studyTimeDate', methods=('GET', 'POST'))
def study_time_date():
    if request.method == "POST":
        res = {
            "version": "2.0",
            "resultCode": "OK",
            "output": {},
        }
        params = request.get_json()
        day = params["action"]["parameters"]["day"]["value"]
        timer_ref = db.collection('StudyTimer')
        today = datetime.now()
        if day == "TODAY":
            query_ref = timer_ref.where('date', '==', today.strftime("%Y-%m-%d"))
            date = "오늘"
        elif day == "YESTERDAY":
            query_ref = timer_ref.where('date', '==', (today+timedelta(days=-1)).strftime("%Y-%m-%d"))
            date = "어제"
        elif day == "B_YESTERDAY":
            query_ref = timer_ref.where('date', '==', (today+timedelta(days=-2)).strftime("%Y-%m-%d"))
            date = "엊그제"
        else:
            res["resultCode"] = "error_unsupported_date"
            return res
        
        if "date_sbj" in params["action"]["parameters"]:
            sbj = params["action"]["parameters"]["date_sbj"]["value"]
            if sbj == "한국사" or sbj == "한능검":
                query_ref = query_ref.where('subject', '==', 'History')
                sbj = "한능검"
            elif sbj == "토익":
                query_ref = query_ref.where('subject', '==', "Toeic")
            elif sbj == "컴활":
                query_ref = query_ref.where('subject', '==', "CS")
        else:
            sbj = "전체 과목"
        
        time_diff = 0
        for query in query_ref.get():
            dic = query.to_dict()
            if 'finish_time' in dic:
                time_diff += dic['finish_time'] - dic['start_time']
        
        if day == "TODAY":    
            stat = db.collection('User').document(USER_TOKEN).get({'is_studying'}).to_dict()
            if stat and stat['is_studying']:
                start_time = int(stat["is_studying"])
                now = int(round(time.time() * 1000))
                time_diff += now - start_time
        res["output"]["hour_date"] = math.floor(((time_diff / (1000 * 60 * 60 )) % 24 ))
        res["output"]["minute_date"] = math.floor(((time_diff / (1000 * 60 )) % 60 ))
        res["output"]["second_date"] = math.floor((time_diff / 1000 ) % 60)
        res["output"]["date"] = date
        res["output"]["sbj_date"] = sbj
        return res
    
@app.route('/studyTimeNow', methods=('GET', 'POST'))
def study_time_now():
    if request.method == "POST":
        res = {
            "version": "2.0",
            "resultCode": "OK",
            "output": {},
        }
        stat = db.collection('User').document(USER_TOKEN).get({'is_studying'}).to_dict()
        if not stat or not stat['is_studying']:
            res["resultCode"] = "error_already_finished"
        else:
            start_time = int(stat["is_studying"])
            now = int(round(time.time() * 1000))
            time_diff = now - start_time
            res["output"]["hour"] = math.floor(((time_diff / (1000 * 60 * 60 )) % 24 ))
            res["output"]["minute"] = math.floor(((time_diff / (1000 * 60 )) % 60 ))
            res["output"]["second"] = math.floor((time_diff / 1000 ) % 60)
        return res


@app.route('/finishTimer', methods=('GET', 'POST'))
def finish():
    if request.method == "POST":
        res = {
            "version": "2.0",
            "resultCode": "OK",
            "output": {},
        }
        stat = db.collection('User').document(USER_TOKEN).get({'is_studying'}).to_dict()
        if not stat or not stat['is_studying']:
            res["resultCode"] = "error_already_finished"
        else:
            millis = int(round(time.time() * 1000))
            user_ref = db.collection('User').document(USER_TOKEN)
            user_ref.update({
                'is_studying': 0
            })
            timer_ref = db.collection('StudyTimer').document(f"{USER_TOKEN}_{stat['is_studying']}")
            timer_ref.update({
                'finish_time': millis
            })
        return res


@app.route('/startTimer', methods=('GET', 'POST'))
def start():
    if request.method == "POST":
        res = {
            "version": "2.0",
            "resultCode": "OK",
            "output": {},
        }
        stat = db.collection('User').document(USER_TOKEN).get({'is_studying'}).to_dict()
        if stat and stat['is_studying']:
            res["resultCode"] = "error_already_started"
        else:
            date = datetime.now().strftime("%Y-%m-%d")
            millis = int(round(time.time() * 1000))
            params = request.get_json()
            sbj = params["action"]["parameters"]["start_sbj"]["value"]
            if sbj == "한국사" or sbj == "한능검": sbj = "History"
            elif sbj == "토익": sbj = "Toeic"
            elif sbj == "컴활": sbj = "CS"
            timer_ref = db.collection('StudyTimer').document(f"{USER_TOKEN}_{millis}")
            timer_ref.set({
                'date': date,
                'start_time': millis,
                'subject': sbj
            })
            user_ref = db.collection('User').document(USER_TOKEN)
            user_ref.update({
                'is_studying': millis
            })
        return res
    
    
@app.route('/health', methods=('GET', 'POST'))
def init():
    if request.method == "POST":
        return 200
        

if __name__=="__main__":
    cred = credentials.Certificate("serviceAccount.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    USER_TOKEN = os.environ.get("GG_TOKEN")
    app.run(port="8080", debug=True)

