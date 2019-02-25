import copy
import http.cookiejar
import json
import logging
import socket
import threading
import time
import urllib.parse
import urllib.request

#import pandas as pd
import socks
from bs4 import BeautifulSoup

from info import name, pwd
from setting import CONCURRENT_REQUEST, TIMEOUT, DELAY, USE_SOCKS5_PROXY, SOCKS5_PROXY_PORT

class course_selector:
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    cas_url = 'https://cas.sysu.edu.cn/cas/login?service=https://uems.sysu.edu.cn/jwxt/api/sso/cas/login%3Fpattern=student-login'
    captcha_url = 'https://cas.sysu.edu.cn/cas/captcha.jsp'
    selection_url = 'https://uems.sysu.edu.cn/jwxt/mk/courseSelection/'
    courselist_url = 'https://uems.sysu.edu.cn/jwxt/{}?_t={}'
    course_select_url = 'https://uems.sysu.edu.cn/jwxt/choose-course-front-server/classCourseInfo/course/choose?_t={}'
    headers = {'User-Agent' : user_agent}
    info_para = ('student-status/student-info/detail', 
        'choose-course-front-server/classCourseInfo/selectCourseInfo',
        'choose-course-front-server/stuCollectedCourse/getYearTerm')

    def __init__(self):
        logging.basicConfig(
            filename='log3.log',
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        self.name = None
        self.pwd = None
        self.course_list = None
        self.exec_code = None
        if USE_SOCKS5_PROXY:
            socks.set_default_proxy(socks.SOCKS5, "localhost", SOCKS5_PROXY_PORT)
            socket.socket = socks.socksocket

    # a safe opener.open(cas_get)
    def __open_s(self, req):
        try:
            response = self.opener.open(req, timeout=TIMEOUT)
            content = response.read()
            try: 
                content = content.decode(encoding='UTF-8')
            except:
                pass # kepp it what it was, like capcha img
            finally:
                response_dict = {
                    'read' : content,
                    'url' : response.geturl(),
                    'info' : response.info()
                }
                logging.debug(response_dict['read'])
                return response_dict
        except urllib.error.HTTPError as e:
            err_dict = {
                'read' : e.read().decode(encoding='UTF-8'),
                'code' : e.code,
                'reason' : e.reason
            }
            logging.debug('err_code={}, err_reason={}, err_msg={}'.format(err_dict['code'], err_dict['reason'], err_dict['reason']))
            return err_dict
        except (socket.timeout, urllib.error.URLError):
            logging.debug('timeout')
            return None

    def __current_time(self):
        return int(time.time())
    
    def __courselist_headers(self, t):
        cl_header = { 
            'User-Agent' : self.user_agent,
            'lastAccessTime': t * 1000 + 213,
            'Content-Type': 'application/json;charset=UTF-8', #MUST have
            'Origin': 'https://uems.sysu.edu.cn',
            'Referer': 'https://uems.sysu.edu.cn/jwxt/mk/courseSelection/'
        }
        return cl_header

    # get exec code and return captcha img
    def pre_login(self):
        # find CAS execution code
        cas_get = urllib.request.Request(self.cas_url, headers=self.headers)
        response = self.__open_s(cas_get)
        if response != None and 'code' not in response:
            html = response['read']
        else:
            raise NameError('visit cas failed')
        soup = BeautifulSoup(html, features="lxml")
        execution = soup.find_all('input', attrs={'name': 'execution'})[0]['value']
        self.exec_code = execution
        # get captcha img
        captcha_get = urllib.request.Request(self.captcha_url, headers=self.headers)
        response = self.__open_s(captcha_get)
        if response != None and 'code' not in response:
            img = response['read']
            return img
        else:
            raise NameError('get captcha failed')

    # build login post and login
    def in_login(self, username, pwd, captcha_str):
        # build login post and login to CAS, update cookie jar
        value = {
            'username' : username,
            'password' : pwd,
            'captcha': captcha_str,
            'execution' : self.exec_code,
            '_eventId' : 'submit',
            'geolocation': ''
        }
        data = urllib.parse.urlencode(value).encode()
        req_post = urllib.request.Request(self.cas_url, headers=self.headers, data=data)
        response = self.__open_s(req_post)
        # TODO:login to CAS error handling, wrong captcha or something else
        #html = response.read()
        #soup = BeautifulSoup(html, features="lxml")
        #title = soup.find_all('title')[0]
        #logging.debug(title)

    # simulate what SYSU course selection system do
    # get session cookie
    def post_login(self):
        # login to course selection system, update cookie jar
        selection_get = urllib.request.Request(self.selection_url, headers=self.headers)
        response = self.__open_s(selection_get)
        # TODO: error handling
        # get personal info
        for para in self.info_para:
            courselist_req_post = urllib.request.Request(self.courselist_url.format(para, self.__current_time()), headers=self.headers)
            response = self.__open_s(courselist_req_post)
            if response != None and 'code' not in response:
                pass
            else:
                raise NameError('query course failed')
            logging.debug(response['read'])
    
    def course_query(self):
        #payload config:
        # pageSize: the maximun number of course the server will return
        # 专必 specialty compulsory: selectedCate=11;selectedType=1;
        # 专选 specialty Elective: selectedCate=21;selectedType=1;
        # 体育 PE: selectedCate=10;selectedType=3;
        # TODO: expand query to all catagories
        query_payload = '{"pageNo":1,"pageSize":20,"param":{"semesterYear":"2018-2","selectedType":"1","selectedCate":"21","hiddenConflictStatus":"0","hiddenSelectedStatus":"0","collectionStatus":"0"}}'
        data = query_payload.encode()
        current_time = self.__current_time()
        courselist_req_post = urllib.request.Request(
            self.courselist_url.format('choose-course-front-server/classCourseInfo/course/list',
            current_time), data=data, headers=self.__courselist_headers(current_time))
        response = self.__open_s(courselist_req_post)
        if response != None and 'code' not in response:
            courselist_str = response['read']
        else:
            raise NameError('query course failed')
        courselist_json = json.loads(courselist_str)
        course_data = courselist_json['data']['rows']

        simplified_course_data_dict = [{
            'cid' : x['courseNum'],
            'cname' : x['courseName'],
            'lecturer' : x['teachingTimePlace'].split(';')[0],
            'sid' : x['teachingClassId'],
            'snum' : '{}/{}'.format(x['courseSelectedNum'], x['baseReceiveNum']),
            'status' : True if x['selectedStatus'] == '4' else False
        } for x in course_data]

        simplified_course_data = [[x['courseNum'], x['courseName'],x['teachingTimePlace'].split(';')[0], x['teachingClassId'], '{}/{}'.format(x['courseSelectedNum'], x['baseReceiveNum']), x['selectedStatus']] for x in course_data]
        self.course_list = simplified_course_data

        #print(pd.DataFrame(simplified_course_data, columns=['Course ID', 'Course Name', 'Lecturer', 'Selete ID', 'Seleted/All', 'Chosen']))

        return simplified_course_data_dict

    class course_select_thread (threading.Thread):
        def __init__(self, course_selector, select_id, selete_type, select_cate):
            threading.Thread.__init__(self)
            self.course_selector = course_selector
            self.select_id = select_id
            self.selete_type = selete_type
            self.select_cate = select_cate

        def run(self):
            self.course_selector.course_select(self.select_id, self.selete_type, self.select_cate)

    # clazzId=teachingClassId
    # 专必: selectedCate=11;selectedType=1;
    # 专选: selectedCate=21;selectedType=1;
    # 体育: selectedCate=10;selectedType=3;
    def course_select(self, select_id, selete_type, select_cate):
        choose_payload = {"clazzId":str(select_id),"selectedType":str(selete_type),"selectedCate":str(select_cate),"check":True}
        choose_payload = json.dumps(choose_payload)
        data = choose_payload.encode()
        while True:
            current_time = self.__current_time()
            choose_req_post = urllib.request.Request(
                self.course_select_url.format(current_time), data=data, headers=self.__courselist_headers(current_time))
            response = self.__open_s(choose_req_post) # will get an json in res['read']
            if response != None:
                response_data = json.loads(response['read'])
                if response_data['code'] == 200 or response_data['code'] == 52021104: # success or already selected
                    print('success, exiting tread')
                    break
            time.sleep(DELAY)

    def course_select_wrapper(self, target_course_list_str):
        target_course_id_list = [x.strip() for x in target_course_list_str.split(',')]
        target_select_id_list = []
        for cid in target_course_id_list:
            for x in self.course_list:
                if x[0] == cid:
                    target_select_id_list.append(x[3])
        if len(target_course_id_list) != len(target_select_id_list):
            pass
            #TODO:error input handling
        else:
            thread_pool = []
            for sid in target_select_id_list:
                for i in range(CONCURRENT_REQUEST):
                    thread = self.course_select_thread(self, sid, 1, 21) #TODO:add different categories support
                    thread.start()
                    thread_pool.append(thread)
            for t in thread_pool:
                t.join()
