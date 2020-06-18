import requests, pickle

def generate_session():
    login_data={'utf8':'%E2%9C%93','name':'chiupc94','password_m':'3514ddfbf9dfc148ac201899397e2d70'}
    session = requests.Session()
    session.post('http://www.shareinvestor.com/user/do_login.html?use_https=0', login_data)
    with open('session', 'wb') as f:
        pickle.dump(session.cookies, f)
    return session
        
        
def read_session():
    session = requests.session()  # or an existing session
    with open('session', 'rb') as f:
        session.cookies.update(pickle.load(f))
    return session