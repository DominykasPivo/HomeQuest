# HomeQuest

The HomeQuest system is a web browser based system that allows users to search and list
properties. The “seller” has two options for types of accounts, gold, which allows the user to
list an unlimited number of properties and normal which allows him only two properties per
user. The system also supports bilingual users, offering two languages English and Deutsch
(German). The “buyer” is able to browse for homes using the filters provided by the system, and also a
trend like system is implemented. This type of user is allowed to look for homes for buying
or renting.

## Getting Started

### Dependencies

* Prerequisites:
    * Operating System: Windows 10 or higher
    * Python: Python 3.8 or higher 
    * Internet Connection: For downloading required libraries and running the project

* Required libraries (can be found in requirements.txt):
    * asgiref
    * crispy-bootstrap5
    * Django
    * django-crispy-forms
    * factory_boy
    * Faker
    * phonenumbers
    * pillow
    * sqlparse
    * tzdata
    * django_two_factor_auth
    * django_otp

### Installing
* Installation Steps:
1. Have an up to date python version
2. Download the Application 
1- Download the source code from github 
2- Extract the ZIP file to a directory of your choice
3. Create a virtual environment in the first HomeQuest directory (Optional):
```
    1. python -m venv venv
```
```
    2. venv/Scripts/activate
```
4. Install required libraries from requirements.txt:
```
    pip install -r requirements.txt 
```
### Executing Program
#### 1. Start the Server
*   1- Open Command Prompt
*   2- Navigate to the application directory:
```
    cd path\to\HomeQuest\HomeQuest
```
*   3- Setup the database and migrations:
```
    1. python manage.py makemigrations
```
```
    2. python manage.py migrate 
```
*   4- Run the server:
```
    python manage.py runserver
```
#### 2. Use the Application
*   1- Use a browser and enter this url to access the website: http://127.0.0.1:8000/
*   2- Register a new account or login with existing credentials
*   3- Search or list properties. 

## Help
*  If you see ModuleNotFoundError, make sure all dependencies are installed.
*  If you have database errors, ensure migrations have been applied.
## Authors

* DominykasPivo
github - [@DominykasPivo](https://github.com/DominykasPivo) 
* HennessyTino
github - [@HennessyTino](https://github.com/HennessyTino) 
* YoussefBahaa1 
github - [@YoussefBahaa1](https://github.com/YoussefBahaa1)
* AtillaBenligil 
github - [@AtillaBenligil](https://github.com/AtillaBenligil)

## Version Control

The project has multiple branches that were used as version control. The list will indicate the branches ordered by oldest to newest with their functionalities:

1. first-branch:
Contains the initial django framework standard setup.
2. login/register:
Contains user functionalities such as login/register...
3.  front-end:
Used for front-end development purposes when the login/register or other branches were still being implemented.
4. property-handling:
Contains the previous login/register branch functionalities and expands towards property handling.
5. code-restructure:
Used to reorganise and error handle the code pulled from property-handling branch.
6. main-branch:
Contains stable, production-ready code. 

## License
This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License - see the LICENSE.md file for details

## Acknowledgments
Inspiration, code snippets, etc.
* [https://www.youtube.com/watch?v=YA4ZPKTPicw&ab_channel=Pyplane](https://www.youtube.com/watch?v=YA4ZPKTPicw&ab_channel=Pyplane)
* [https://medium.com/@patelaniket1207/building-a-multi-language-website-with-django-a-comprehensive-guide-f6b9017c8bde](https://medium.com/@patelaniket1207/building-a-multi-language-website-with-django-a-comprehensive-guide-f6b9017c8bde)
* [https://www.w3schools.com/django/django_getstarted.php](https://www.w3schools.com/django/django_getstarted.php)
* [https://testdriven.io/blog/django-custom-user-model/](https://testdriven.io/blog/django-custom-user-model/)
* [https://factoryboy.readthedocs.io/en/stable/orms.html](https://factoryboy.readthedocs.io/en/stable/orms.html)
* [https://wellfire.co/learn/using-django-proxy-models/](https://wellfire.co/learn/using-django-proxy-models/)
* [https://www.youtube.com/watch?v=GNsuF4xB80E&ab_channel=DaveGray](https://www.youtube.com/watch?v=GNsuF4xB80E&ab_channel=DaveGray)
* [https://dev.to/doridoro/django-model-properties-28ac](https://dev.to/doridoro/django-model-properties-28ac)
* [https://www.w3schools.com/django/django_admin_create_user.php](https://www.w3schools.com/django/django_admin_create_user.php)
* [https://djangocentral.com/authentication-using-an-email-address/](https://djangocentral.com/authentication-using-an-email-address/)
* [https://www.youtube.com/watch?v=QgBrKVpIrgU&ab_channel=VeryAcademy](https://www.youtube.com/watch?v=QgBrKVpIrgU&ab_channel=VeryAcademy)
* [https://django-flexible-subscriptions.readthedocs.io/en/latest/installation.html](https://django-flexible-subscriptions.readthedocs.io/en/latest/installation.html)
* [https://widyantohadi.medium.com/make-your-django-project-less-confusing-with-design-pattern-89a5232be4f3](https://widyantohadi.medium.com/make-your-django-project-less-confusing-with-design-pattern-89a5232be4f3)