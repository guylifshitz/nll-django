# newspaper-language-learner-django

This is the website component of the newspaper langauge learner project. 
The data is prepared using this project: https://github.com/guylifshitz/newspaper-language-learner

It uses the Django framework.

## Setup environment 

Install python libraries with 

```pip3 install -r requirements.txt```

You will need to have two environment variables (set the values in [ ] based on your environment)

```
export NLL_DJANGO_DB_PASS=[PASSWORD]
export NLL_DJANGO_SECRET_KEY=[SECRET KEY]
```


## Running 

To run on localhost use 
```
cd /Users/guy/guy/project/nll/newspaper-language-learner-django
python3 manage.py runserver
```


