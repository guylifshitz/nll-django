
export NLL_DJANGO_DB_PASS=eYZNkYwqxpBFVrsxTJdYkSmyYGEtMaxVPcgaRRWUuhTZwXPbyd
export NLL_DJANGO_SECRET_KEY=YNYwxFVrxdkmGtaPc
cd /Users/guy/guy/project/nll/newspaper-language-learner-django
python3 manage.py runserver



sudo docker-compose -f docker-compose-works-staging.yml up


- UPDATE HTTPS certificate!!!!!
- cleanup files
    -   accoutns OK
    - API / urls 
    - articles / views BIGGIE
    - static folder
- write tests (use codium AI)
- check api/urls special characters common ?????? whats this
- Reelease prettyness
    - write README
    - update requirements.txt
- arabic support
    - check language_code instead of languge doesnt mess stuff up
    - fix flexion shwing in arabic on flashcards
    - similar words finder
    - api (urls.py)
    - better code to find langauge in javascrip from url
- dont let range be more than 500?



OLD TODO (still relevant)
- fix backup 
- auto certificate
- make update work without guy using laptop
- fix azure translation
- post
- cleanup code   (clean code, and copy code from server)
    - docker stuff as github

sudo certbot certonly --standalone --agree-tos --no-eff-email -d guylifshitz.com -d www.guylifshitz.com -d language.guylifshitz.com --rsa-key-size 4096
zip -r letsencryt.zip /etc/letsencrypt/
sudo cp /etc/letsencrypt/live/guylifshitz.com/fullchain.pem fullchain.pem
sudo cp /etc/letsencrypt/live/guylifshitz.com/privkey.pem privkey.pem

sudo cp /etc/letsencrypt/live/guylifshitz.com/fullchain.pem code/fullchain.pem
sudo cp /etc/letsencrypt/live/guylifshitz.com/privkey.pem code/privkey.pem

sudo docker build . -t docker-django_web
sudo docker build . -t docker-django_web --no-cache

sudo docker-compose -f docker-compose-works.yml up

gunicorn -w 4 -b :443 --certfile /certs/fullchain.pem --keyfile /certs/privkey.pem hello:app
gunicorn news_reader.wsgi:application --bind 0.0.0.0:443 -w 4  --certfile fullchain.pem --keyfile privkey.pem

sudo ln -s /etc/letsencrypt/live/guylifshitz./fullchain.pem fullchain.pem
sudo ln -s /etc/letsencrypt/live/guylifshitz.com/privkey.pem privkey.pem



guy@vps536496:~/newspaper-language-learner/docker-django$ sudo docker build . -t docker-django_web




Hello, 

I am excited to share a website to help learn hebrew that I have created. 
I have been using/developping this website privately over the last year and have found it super useful. 

- save words you know.
- find hebrew news article titles with lots of words you know, so you can practice those words.
- option to translate words you don't know to English, so you can focus on words you want to practice.
- other features to try out (text to speech, similar roots/words, etc...)

I've made this video tutorial to show off the use of the site.


I am actively developing the site and would really appreciate any feedback to imrpove and add funcitonalities.

If you would like to help out, the website is Open Source, and could use skills in Python, Javascript, CSS and Hebrew language parsing (currently using YAP). 
You can email me for more info.

I am planning on making an arabic version of the site very soon.

I'm not amazing with designing websites, so please by kind, and don't hestitate to ask questions if something isn't intuitive.






Eingestin
technology axe



ه ج م