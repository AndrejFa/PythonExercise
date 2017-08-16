from passlib.hash import pbkdf2_sha256
import getpass
import csv
import ast
from statistics import mean


def main():
    choice = logger()
    if choice == 1:
        register()
        user = log_in()
    else:
        user = log_in()
        # user is not yet registered
        if user == True:
            user = log_in()

    platform(user)

    operation = selection("What would you like to do today? (chose number): ", ("1", "2", "3", "4"))
    file_path = user + "_students.csv"
    student = Student(file_path)

    while operation != 4:
        if operation == 1:
            name = input("Student name: ")
            grade = get_grade()
            print("Adding grade...")
            student.add_grade(name, grade)
            student.print_grades()
        elif operation == 2:
            name = input("Which student you want to remove? ")
            student.remove_student(name)
            student.print_grades()
        elif operation == 3:
            name = input("Which student grade average you want to calculate? ")
            student.average_grade(name)

        operation = selection("What would you like to do next? (chose number): ", ("1", "2", "3", "4"))

    # admin session is finished, update admin student information
    student.update_session(file_path)


class Student:
    """
    Class that contains information for each admin students and corresponding student grades.
    Admin can add grade for specified student, remove student from database and
    calculate student grade average.
    """

    def __init__(self, file_path):
        """
        initialize admin students information
        """
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            self.student_grades = dict(reader)
        self.student_grades = {key: ast.literal_eval(val) for key, val in self.student_grades.items()}

    def add_grade(self, student, grade):
        """
        enter grade for student
        """
        if student not in self.student_grades:
            self.student_grades[student] = [grade]
        else:
            self.student_grades[student].append(grade)

    def remove_student(self, student):
        """
        remove student from disctionary
        """
        if self.student_grades.get(student):
            self.student_grades.pop(student)
        else:
            print("Student {} is not in a database!".format(student))

    def average_grade(self, student):
        """
        calculate average student grade
        """
        values = self.student_grades.get(student)
        if values:
            print("{} grade average is {:.2f}.".format(student.capitalize(), mean(values)))
        else:
            print("Student {} is not in a database!".format(student))

    def print_grades(self):
        """
        print information about admin students grades
        """
        print(self.student_grades)

    def update_session(self, file_path):
        """
        update admin students information on exit from current session
        """
        with open(file_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in self.student_grades.items():
                writer.writerow([key, value])


def platform(username):
    print("\tWelcome {} to Grade Central\n".format(username.capitalize()))
    print("\t[1] - Enter Grades")
    print("\t[2] - Remove Student")
    print("\t[3] - Student Average Grades")
    print("\t[4] - Exit\n")


def selection(text, choice):
    """
        Function that check for correct selection
        return integer
    """
    option = input(text)
    while option not in choice:
        option = input("Retry: ")
    return int(option)


def get_grade():
    """
    function that ask admin for student grade and check if can be converted to int
    return integer
    """
    grade = input("Grade: ")
    while True:
        try:
            grade = int(grade)
        except ValueError:
            print("Grade has to be a number!")
            grade = input("Retry: ")
            continue
        else:
            if grade < 0 or grade > 100:
                print("Grade has to be in interval [0,100]!")
                grade = input("Retry: ")
                continue
            break
    return grade


def logger():
    """
    Function that prompt user for registration or log in
    return integer
    """
    print("[1] Register")
    print("[2] Log In")
    return selection("Select number: ", ("1", "2"))


def get_username_and_password(registration=False):
    """
    function that prompt user for username and password
    return tuple
    """
    username = input("username: ")
    password = get_password("password: ")
    if registration:
        password = pbkdf2_sha256.hash(password)
    return(username, password)


def get_password(text):
    """
    Function that prompt user for password
    return string
    """
    return getpass.getpass(text)


def in_database():
    """
    User misstype logger values and is already registered 
    return string
    """
    already_registered = input("Are you already registered? (y/n) ")
    while already_registered not in ("y", "n"):
        already_registered = input("Retry: ")
    return already_registered


def register():
    """
    Function that enables user to register for the first time. 
    It takes username and password as input and save it to the csv file.
    """
    print("Registration!\n")
    username, password = get_username_and_password(True)
    with open("admin.csv", "r+") as admin:
        admins = dict([row.rstrip().split(",") for row in admin.readlines()])
        # do not allow duplicated username
        while username in admins:
            print("Username already exists!")
            if in_database() == "y":
                return
            username, password = get_username_and_password(True)
        admin.write(username + "," + password + "\n")
    print("Registered successful.\n")
    # create a file on disc for a user students
    file_name = username + "_students.csv"
    f = open(file_name, "w")
    f.close()


def log_in():
    """
    Function that log in user into Student platform.
    """
    print("Log in!\n")
    username, password = get_username_and_password()
    with open("admin.csv") as admin:
        admins = dict([row.rstrip().split(",") for row in admin.readlines()])
        # not registered user
        if username not in admins:
            print("You are not registered!")
            register()
            return True

        while not pbkdf2_sha256.verify(password, admins[username]):
            print("Invalid password")
            password = get_password("Retry: ")
    print("Log in successful!\n")
    return username

if __name__ == "__main__":
    main()
