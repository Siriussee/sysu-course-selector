from scs import course_selector
from info import name, pwd

def main():
    cs = course_selector()
    img = cs.pre_login()
    with open('code.bmp', 'wb') as f:
        f.write(img)
    captcha_str = input('what is captcha?')
    cs.in_login(name, pwd, captcha_str)
    course_data = cs.course_query()
    # print course_data
    print('{:10}{:30}{:10}{:10}{:10}'.format('Course ID', 'Course Name', 'Lecturer', 'Seleted/All', 'Chosen'))
    for cd in course_data:
        print('{:10}{:30}{:10}{:10}{:10}'.format(cd['cid'], cd['cname'], cd['lecturer'], cd['snum'] ,cd['status']))
    target_course_list_str = input('Enter Course ID, separate by ENGILSH comma , :')
    cs.course_select_wrapper(target_course_list_str)

if __name__ == '__main__':
    main()
