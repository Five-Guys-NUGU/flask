import firebase_admin, os, time, math
from flask import Flask, request
from datetime import datetime, timedelta
from firebase_admin import credentials, firestore

app = Flask(__name__)


@app.route('/friendStudyTime', methods=('GET', 'POST'))
def friend_study_time():
    if request.method == "POST":
        res = {
            "version": "2.0",
            "resultCode": "OK",
            "output": {},
        }
        params = request.get_json()
        studymate = db.collection('User').document(USER_TOKEN).get({'studymate'}).to_dict()['studymate']
        query_ref = db.collection('StudyTimer').document(studymate).collection(datetime.now().strftime("%Y-%m-%d"))
        if "friend_sbj" in params["action"]["parameters"]:
            sbj = params["action"]["parameters"]["friend_sbj"]["value"]
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
            if 'finish_time' in dic and dic['finish_time']:
                time_diff += dic['finish_time'] - dic['start_time']
        
        ''' Bug -> Need to fix
        stat = db.collection('User').document(USER_TOKEN).get({'is_studying'}).to_dict()
        if stat and stat['is_studying']:
            start_time = int(stat["is_studying"])
            now = int(round(time.time() * 1000))
            time_diff += now - start_time
        '''
        res["output"]["hour_fst"] = math.floor(((time_diff / (1000 * 60 * 60 )) % 24 ))
        res["output"]["minute_fst"] = math.floor(((time_diff / (1000 * 60 )) % 60 ))
        res["output"]["second_fst"] = math.floor((time_diff / 1000 ) % 60)
        res["output"]["name_fst"] = db.collection('User').document(studymate).get({'name'}).to_dict()['name']
        res["output"]["sbj_fst"] = sbj
        return res


@app.route('/isFriendStudying', methods=('GET', 'POST'))
def is_friend_studying():
    if request.method == "POST":
        res = {
            "version": "2.0",
            "resultCode": "OK",
            "output": {},
        }
        studymate = db.collection('User').document(USER_TOKEN).get({'studymate'}).to_dict()['studymate']
        studymate_stat = db.collection('User').document(studymate).get({'is_studying'}).to_dict()
        res["output"]["friend_name"] = db.collection('User').document(studymate).get({'name'}).to_dict()['name']
        if not studymate_stat or not studymate_stat['is_studying']:
            res["resultCode"] = "error_not_studying"
        else:
            start_time = int(studymate_stat["is_studying"])
            now = int(round(time.time() * 1000))
            time_diff = now - start_time
            res["output"]["friend_hour"] = math.floor(((time_diff / (1000 * 60 * 60 )) % 24 ))
            res["output"]["friend_minute"] = math.floor(((time_diff / (1000 * 60 )) % 60 ))
            res["output"]["friend_second"] = math.floor((time_diff / 1000 ) % 60)
        return res

@app.route('/readNote', methods=('GET', 'POST'))
def read_note():
    if request.method == "POST":
        res = {
            "version": "2.0",
            "resultCode": "OK",
            "output": {},
        }
        params = request.get_json()
        sbj = params["action"]["parameters"]["subject"]["value"]
        sbj_ref = db.collection('NoteTaking').document(USER_TOKEN)
        if sbj == '한능검' or sbj == '한국사':
            query_ref = sbj_ref.collection('History').get()
        elif sbj == '컴활':
            query_ref = sbj_ref.collection('CS').get()
        elif sbj == '토익':
            query_ref = sbj_ref.collection('Toeic').get()
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
        timer_ref = db.collection('StudyTimer').document(USER_TOKEN)
        today = datetime.now()
        if day == "TODAY":
            query_ref = timer_ref.collection(today.strftime("%Y-%m-%d"))
            date = "오늘"
        elif day == "YESTERDAY":
            query_ref = timer_ref.collection((today+timedelta(days=-1)).strftime("%Y-%m-%d"))
            date = "어제"
        elif day == "B_YESTERDAY":
            query_ref = timer_ref.collection((today+timedelta(days=-2)).strftime("%Y-%m-%d"))
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
            if 'finish_time' in dic and dic['finish_time']:
                time_diff += dic['finish_time'] - dic['start_time']
        
        ''' Bug -> Need to Fixed
        if day == "TODAY":    
            stat = db.collection('User').document(USER_TOKEN).get({'is_studying'}).to_dict()
            if stat and stat['is_studying']:
                start_time = int(stat["is_studying"])
                now = int(round(time.time() * 1000))
                time_diff += now - start_time
        '''
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
def finish_timer():
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
            date = datetime.now().strftime("%Y-%m-%d")
            timer_ref = db.collection('StudyTimer').document(USER_TOKEN).collection(date).document(f"{USER_TOKEN}_{stat['is_studying']}")
            timer_ref.update({
                'finish_time': millis
            })
        return res


@app.route('/startTimer', methods=('GET', 'POST'))
def start_timer():
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
            timer_ref = db.collection('StudyTimer').document(USER_TOKEN).collection(date).document(f"{USER_TOKEN}_{millis}")
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
    
    
@app.route('/health')
def health():
    return "200 OK"


@app.route('/')
def hello():
    return "Hello, this is StudyBNB"


if __name__=="__main__":
    cred = credentials.Certificate("serviceAccount.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    USER_TOKEN = "aGqlgMvfgVcTszooEtmtdXrQLuU2"
    app.run(host='0.0.0.0', port=5000)

