from scs import course_selector
from info import name, pwd

def main():
    cs = course_selector()
    cs.pre_login()
    cs.in_login(name, pwd)
    course_data = cs.course_query()
    # print course_data
    print('{:10}{:30}{:10}{:10}{:10}'.format('Course ID', 'Course Name', 'Lecturer', 'Seleted/All', 'Chosen'))
    for cd in course_data:
        print('{:10}{:30}{:10}{:10}{:10}'.format(cd['cid'], cd['cname'], cd['lecturer'], cd['snum'] ,cd['status']))
    target_course_list_str = input('Enter Course ID, separate by ENGILSH comma , :')
    cs.course_select_wrapper(target_course_list_str)

if __name__ == '__main__':
    main()
