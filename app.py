from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import timedelta
import numpy as np
import random
import time
from Algorithm import SM4, gen_r, gen_si, GetEi, threshold_GStern_com_resp, threshold_GStern_verify,link_sign , get_key
from Mysql_function import Mysql as sql
from hashlib import md5

app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)  # Session timeout set to 5 minutes

# UPLOAD_FOLDER = 'uploads'
# def create_upload_folder(app):
#     upload_folder = os.path.join(app.instance_path, UPLOAD_FOLDER)
#     os.makedirs(upload_folder, exist_ok=True)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# create_upload_folder(app)

n = 1268
w = 25
k = 951
t = 300

def is_admin_logged_in():
    return 'identity' in session

def is_user_logged_in():
    return 'username' in session

@app.route('/')
def home():
    if is_admin_logged_in():
        if session['identity'] == "managing":
            return redirect(url_for('manage'))
        else:
            return redirect(url_for('dashboard'))
    elif is_user_logged_in():
        return redirect(url_for('vote'))
    return render_template('login.html')

progress = 0
@app.route('/vote/add_members', methods=['GET', 'POST'])
def add_members():
    global progress
    progress = 0
    if not is_user_logged_in():
        return redirect(url_for('home'))
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            if uploaded_file.filename.endswith('.csv'):
                uploaded_file.save(uploaded_file.filename)
                with open(uploaded_file.filename, 'r', encoding='utf-8') as f:
                    users = f.readlines()[1:]
                    total_groups = len(users)

                users_group = []
                count_user = {}
                ei_dir = {}
                eis_dir = {}
                sis_dir = {}
                all_e = {}
                all_s = {}
                count = 0
                i = 0
                for user in users:
                    user = user.strip().split(',')
                    users_group.append(user[-1])
                tmp_user = set(users_group)
                while len(tmp_user):
                    tmp = tmp_user.pop()
                    count_user[tmp] = users_group.count(tmp)
                for gname, gnums in count_user.items():
                    ei_dir[gname] = GetEi(gnums)
                    eis_dir[gname] = []
                    sis_dir[gname] = []
                    sql.update(f"update `group` set membernums = '{gnums}' where groupname='{gname}'")
                for user in users:
                    secretGenerateTime = time.perf_counter()
                    user = user.strip().split(',')
                    ei = ei_dir.get(user[-1]).get_ei(int(user[0]))
                    eis_dir[user[-1]].append(ei)
                    si = gen_si(n, k, ei)
                    sis_dir[user[-1]].append(si)
                    i += 1
                    sql.update(
                        f"insert into `users` (`uid`,`username`,`belong`) values ('{user[0]}','{user[1].lower()}','{user[2]}')")
                    # 更新进度
                    secretGenerateTime_end = time.perf_counter()
                    progress = int((i / total_groups) * 100)
                    print("密钥生成时间:","{:.10f}".format(secretGenerateTime_end - secretGenerateTime))
                    # print(f"Current progress: {progress}%")  # 用于调试
                                        
                tmp_list = [i for i in range(n - 1)]
                for key in eis_dir.keys():
                    
                    chosen_vote_ids = random.sample(tmp_list, t)
                    all_e[key] = [eis_dir[key][j] for j in chosen_vote_ids]
                    all_s[key] = [sis_dir[key][j] for j in chosen_vote_ids]
                    sql.update(
                        f"update `group` set e='{np.array(all_e[key])}',s='{np.array(all_s[key])}'where groupname='{key}'")
                    r, G = gen_r(n, t, all_e[key], all_s[key])
                    member = f'{np.array([i + count * n for i in chosen_vote_ids])}'
                    sql.update(
                        f"update `group` set r='{r}',member='{member}',G='{G}' where groupname='{key}'")
                    H = np.random.randint(0, 2, (n - k, n))
                    sql.update(
                        f"update `group` set member='{member}',H='{H}' where groupname='{key}'")
                    for i in chosen_vote_ids:
                        sql.update(
                            f"update `users` set ri='{r[chosen_vote_ids.index(i)]}' where uid='{i + count * n}'")
                    count += 1
                    
                    print("密钥生成时间:","{:.10f}".format(secretGenerateTime_end - secretGenerateTime))
                flash('添加组员成功！')
                return redirect(url_for('vote'))
            else:
                flash('错误的文件格式，请上传csv文件！', 'danger')
                return redirect(url_for('add_members'))
    return render_template("add_members.html")

@app.route('/vote/progress')
def get_progress():
    global progress
    print(f"Returning progress: {progress}%")  # 用于调试
    return jsonify(progress=progress)

class Sign():
    def __init__(self, e, H, G , tid):
        super().__init__()
        self.e = e
        self.H = H
        self.G = G
        self.tid = tid
        self.sql=sql()

    def run(self) -> None:
        e = self.getvalue(self.e)
        G = self.getvalue(self.G)
        H = self.getvalue(self.H)
        index = self.tid
        group_name = session['groupname']
        com1_1, com2_1, resp1_1, resp2_1 = threshold_GStern_com_resp(n, H, G, e, 0, t)
        self.sql.update(
            f"update `group` set com1_1='{com1_1}',com2_1='{com2_1}'where groupname='{group_name}'")
        self.sql.update(f"update `group` set resp1_1='{np.array(resp1_1)}'where groupname='{group_name}'")
        self.sql.update(f"update `group` set resp2_1='{np.array(resp2_1)}'where groupname='{group_name}'")
        had_voter = self.sql.query(f"select isvoters from vote_contents")
        # print(int(index))
        # print(had_voter[index-1]['isvoters'])
        isvoters = had_voter[index-1]['isvoters'] + group_name
        self.sql.update(f"update `vote_contents` set isvoters='{isvoters}'where tid={index}")
        sign_state = 1
        return sign_state

    def getvalue(self, str):
        lis = []
        for i in str[1:].split(']')[:-2]:
            a = [int(j) for j in i.strip()[1:].split()]
            lis.append(a)
        return np.array(lis)
        

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if not is_user_logged_in():
        return redirect(url_for('home'))
    if ("admin" in session['username']):
        return redirect(url_for('home'))
    valid_themes = []
    themes = sql.query("SELECT tid, themes,isvoters FROM vote_contents")
    for theme in themes:
        if 'vote_good' not in theme['isvoters']:
            # print(theme)
            valid_themes.append(theme)
    themes = valid_themes
    # print(themes)
    username = session['username'] 
    group_name = session['groupname']
    if request.method == 'POST':
        if username:
            global index
            index = int(request.form['theme'])
            content = request.form['content']
            sign_time = time.perf_counter()
            sm4 = SM4()
            realykey, result = get_key(sql=sql,group_name=group_name)
            xx = sql.query(f"select user_submit from vote_contents where tid={index}")
            user_submit = xx[0]['user_submit']+f'{group_name}:{sm4.encryptSM4(realykey, content)},' if xx[0]['user_submit'] else f'{group_name}:{sm4.encryptSM4(realykey, content)},'
            sql.update(f"update `vote_contents` set user_submit='{user_submit}' where tid={index}")
            sign = Sign(result['e'], result['H'], result['G'], index)
            sign_state = sign.run()
            # print(sign_state)
            if(sign_state == 1):
                flash('投票成功!')
                sign_time_end = time.perf_counter()
                print('签名时间',"{:.10f}".format(sign_time_end - sign_time))
                return redirect(url_for("vote"))
            else:
                flash('投票失败')
                return redirect(url_for('vote'))
        else:
            flash('未登录！', 'danger')
            return redirect(url_for('home'))
    return render_template('vote.html', themes=themes, group_name = group_name)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = md5(request.form['password'].encode("utf-8")).hexdigest()
        # print(password)
        user_info = sql.query(f"SELECT * FROM `group` WHERE username = '{username}' AND password = '{password}'")
        admin = sql.query(f"SELECT * FROM `management` WHERE username = '{username}' AND password ='{password}'")
        if user_info:
            session.permanent = True  # Make the session permanent upon login
            session['username'] = username
            group_name = user_info[0]['groupname']
            session['groupname'] = group_name
            flash('登陆成功！', 'success')
            return redirect(url_for('vote'))
        elif admin:
            # print(admin['identity'])
            session.permanent = True
            session['username'] = username
            if admin[0]['identity'] == "manage":
                session["identity"] = "manage"
                return redirect(url_for('manage'))
            elif admin[0]['identity'] == "counting":
                session["identity"] = "counting"
                return redirect(url_for('dashboard'))
            else:
                flash('投票权限', 'danger')
                return redirect(url_for('home'))
        else:
            flash('错误的用户名或密码！请重试', 'danger')
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

# 用户注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = md5(request.form['password'].encode("utf-8")).hexdigest()
        groupname = request.form['groupname']
        existing_user = sql.query(f"SELECT * FROM `group` WHERE username ='{username}'")
        uid = sql.query("SELECT uid FROM `group`")
        try:
            uid = int(uid[0]['uid']) + 1
        except:
            uid = 1
        if existing_user:
            flash('用户名已存在，请选择其他用户名。', 'danger')
            return redirect(url_for('register'))
        else:
            sql.update(f"INSERT INTO `group` (uid ,username , groupname , password) VALUES ( '{uid}' , '{username}' ,'{groupname}', '{password}')")
            flash('注册成功！您现在可以登录。', 'success')
            return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/manage',methods=['GET', 'POST'])
def manage():
    if not is_admin_logged_in():
        return redirect(url_for('home'))
    tid = sql.query("select tid from vote_contents")
    # print(tid[-1]['tid'])
    try:
        tid = int(tid[-1]['tid']) + 1
        # print(tid)
    except:
        tid = 1
    if request.method == 'POST':
        themes = request.form['theme']
        deadtime = request.form['deadtime']
        # print(tid,themes,deadtime)
        sql.update(f"insert into vote_contents (tid,themes,deadtime)values ('{tid}','{themes}','{deadtime}')")
        flash('添加主题成功！')
    return render_template('manage.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/dashboard')
def dashboard():
    if not is_admin_logged_in():
        return redirect(url_for('home'))
    username = session['username']
    return render_template('dashboard.html',username = username)

@app.route('/dashboard/verify',methods = ['GET','POST'])
def verify():
    if not is_admin_logged_in():
        return redirect(url_for('home'))
    groups = sql.query("select uid,groupname from `group`")
    themes = sql.query("select isvoters,tid,themes from vote_contents")
    if (request.method =='POST'):
        value = request.form['group']
        uid, groupname = value.split(',', 1)
        theme = request.form['theme']
        tid = theme
        verified_theme = sql.query(f"select isvoters from vote_contents where tid = '{tid}'")[0]
        if (groupname not in verified_theme['isvoters']):
            flash("该组用户未参与投票")
            return redirect(url_for('verify'))
        verify_time = time.perf_counter()
        r = V.run(uid,tid)
        
        if r[0] == '1':
            arr = r.split('-')
            # self.ui.pushButton_register.setText('验证')
            # self.ui.pushButton_register.setEnabled(True)
            result = sql.query(f"select isvalid from vote_contents where tid={int(arr[-1])}")
            isvalid = result[0]['isvalid']+arr[1]+":1," if result[0]['isvalid'] and result[0]['isvalid']!=0 else arr[1]+":1,"
            sql.update(f"update vote_contents set isvalid='{isvalid}' where tid={int(arr[-1])}")
            verify_time_end = time.perf_counter()
            flash("验证成功,本条投票-有效")
            print("验证时间：","{:.10f}".format(verify_time_end - verify_time))
        else:
            flash("验证失败，本条投票-无效")
    return render_template('verify.html',themes = themes,groups = groups)

@app.route('/dashboard/link',methods= ['POST','GET'])
def link():
    if not is_admin_logged_in():
        return redirect(url_for('home'))
    groups = sql.query(f"select uid,groupname from `group`")
    # print(groups)
    if(request.method == 'POST'):
    #    value = request.form
        uid = request.form['groupA']
        uid2 = request.form['groupB']
        # print(uid,uid2)
        flash('链接中...')
        link_time = time.perf_counter()
        r = V.run(uid,uid2)
        # print(r)
        arr = r.split('-')
        # print(arr)
        if int(arr[2]) != 0:
            link_time_end = time.perf_counter()
            flash(f"链接成功，两组中有{arr[2]}人共同参与投票")
            print("签名链接时间：","{:.10f}".format(link_time_end - link_time))
        else:
            flash(f"链接失败，没人共同参与投票")
    return render_template('link.html',groups = groups)

@app.route('/dashboard/show',methods = ['GET','POST'])
def show():
    if not is_admin_logged_in():
        return redirect(url_for('home'))
    username = session['username']
    result = sql.query("select themes,user_submit,isvalid from vote_contents")
    # print(result)
    final_res= ''
    if (request.form.get('tag', 0, type=int)):
        tag = request.form.get('tag', 0, type=int)
    else:
        tag = 0
    final_res = WrittingNotOfOther(tag,result)
    # print(final_res)
    return render_template('show.html',final_res = final_res,username = username)

def WrittingNotOfOther(tag, result):
    final_res = ''
    sm4 = SM4()
    # print(tag)
    if tag == 0:
        for re in result:
            if re['user_submit'] is None:
                continue
            for user in re['user_submit'].split(",")[:-1]:
                user_msg = user.split(":")
                key, _ = get_key(sql(), user_msg[0])
                msg = sm4.decryptSM4(key, user_msg[1])
                if "不同意" in msg or "否认" in msg or "拒绝" in msg or "不可以" in msg or "不认可" in msg or "不认同" in msg or "反对" in msg:
                    res = f"{user_msg[0]}-{re['themes']}-拒绝"
                else:
                    res = f"{user_msg[0]}-{re['themes']}-同意"
                final_res += res + "\n"
        return final_res
                # print(final_res)
    else:
        usernames = {}
        for re in result:
            count = "x"
            usernames[count] = []
            try:
                s = re['isvalid'].split(",")[:-1]
                for i in s:
                    id = i.split(":")[0]
                    name = sql.query(f"select groupname from `group` where uid = '{id}'")
                    usernames.get(count).append(name[0]['groupname'])
            except:
                pass
            finally:
                for user in re['user_submit'].split(",")[:-1]:
                    user_msg = user.split(":")
                    key, _ = get_key(sql, user_msg[0])
                    msg = sm4.decryptSM4(key, user_msg[1])
                    if "不同意" in msg or "否认" in msg or "拒绝" in msg or "不可以" in msg or "不认可" in msg or "不认同" in msg or "反对" in msg:
                        res = f"{user_msg[0]}-{re['themes']}-拒绝"
                    else:
                        res = f"{user_msg[0]}-{re['themes']}-同意"
                    if tag == 1 and user_msg[0] in usernames.get(count):
                        final_res += res + "\n"
                    elif tag == 2 and user_msg[0] not in usernames.get(count):
                        final_res += res + "\n"
            count+="1"
    return final_res

class V():
    sql = sql()
    # _sum = Signal(str)  # 信号类型 str
    def getvalue(str):
        lis = []
        for i in str[1:].split(']')[:-2]:
            a = [int(j) for j in i.strip()[1:].split()]
            lis.append(a)
        return np.array(lis)

    def run(uid,tid):
        result=sql.query(f"select s,r,H,G,com1_1,com2_1,resp1_1,resp2_1 from `group` where uid={uid}")[0]
        s = V.getvalue(result['s'])
        r = V.getvalue(result['r'])
        H = V.getvalue(result['H'])
        G = V.getvalue(result['G'])
        com1_1 = result['com1_1']
        com2_1 = result['com2_1']
        resp1_1 = V.getvalue(result['resp1_1'])
        resp2_1 = V.getvalue(result['resp2_1'])
        index = tid
        rs = sql.query(f"select r from `group` where uid={uid}")[0]
        r2 = V.getvalue(rs['r'])
        re = threshold_GStern_verify(n, H, G, s, r, 0, t, com1_1, com2_1, resp1_1, resp2_1)
        link = link_sign(r,r2)
        # print(",".join(link[1]))
        # # print((str(re)+"-"+str(uid)+"-"+str(link[1])+"-"+",".join(link[0])+"-"+str(index)))
        return str(re)+"-"+str(uid)+"-"+str(link[0])+"-"+str(index)  # 计算结果完成后，发送结果

@app.route('/logout',methods=["GET"])
def logout():
    session.clear()
    flash('退出成功！', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)