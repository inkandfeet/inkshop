# Inkshop is about people.

Inkshop is a human-centered framework for running your website, mailing list, and store all in one.

It doesn't track people, has strong privacy protection for both you and your customers baked in, and Just Works.

Feedback, improvements, and contributions are welcome. :)


## Current Status:

I'm bootstrapping this project on my own site, [Ink and Feet](https://inkandfeet.com). 

I'll be moving from a setup with:
- Static files served by Dreamhost
- Mailing list managed by Ontraport
- Sales managed by Ontraport and Teachery

Current status:

Mailing list is the first thing to build. Target for basic mailing list is April 21, 2019.

This will include:
- Send message to my list
- Unsubscribe
- Love
- Subscribe
- Receive replies


## Bootstrapping

```bash
git clone https://github.com/inkandfeet/inkshop.git
cd inkshop
cp env.sample .env
# Edit .env with your values
docker network create inkshop
docker-compose up
```



## Built on:
- [Simple Crypt](https://pypi.org/project/simple-crypt/) (and [pycrypto](https://pypi.org/project/pycrypto/)) for encryption.
- Mailgun for email sending.
- AWS S3 for uploads and static file serving.
- Postgres for database.
- Redis for caching and queuing.
- Docker for encapsulation and dev ease.
- Heroku for deployment.