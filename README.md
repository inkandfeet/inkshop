
# Inkshop is about people.

Inkshop is a human-centered framework for running your website, mailing list, and store all in one.

It doesn't track people, has strong privacy protection for both you and your customers baked in, and Just Works.

Feedback, improvements, and contributions are welcome. :)


## Project Overview:

I'm bootstrapping this project on my own site, [Ink and Feet](https://inkandfeet.com). 

You can read more about the decision to move to inkshop in [this open letter.]()

I'll be moving from a setup with:
- Static site generated by inkblock, and served by Dreamhost and Cloudflare
- Mailing list managed by Ontraport
- Redirects and url shortening run by inkdots
- Digital product sales managed by Ontraport and Teachery


When it's at 1.0, this project will let you:
- Manage an email list, using best practices for deliverability
- Host a website, with pages and blog posts
- Sell downloadable digital products
- Sell online digital products, including customer authentication and secure data storage
- Understand what pages are generating the most traffic
- Create shortened URLs for sharing with social media
- Share posts to social media via buffer

## Current status:

[![CircleCI](https://circleci.com/gh/inkandfeet/inkshop.svg?style=svg)](https://circleci.com/gh/inkandfeet/inkshop)

It just got started, on April 15 2019.   Mailing list is the first thing to build. Target for basic mailing list is April 21, 2019.

This will include:
- Subscribe
- Send message to my list
- Import
- Unsubscribe
- Love
- Receive replies


## Bootstrapping

```bash
git clone https://github.com/inkandfeet/inkshop.git
cd inkshop
cp env.sample .env
# Edit .env with your values
docker network create inkshop
docker-compose run db createdb inkshop -h db -U $POSTGRES_USER
docker-compose up
```


## Running tests

Tests are wrapped with [polytester](https://github.com/skoczen/polytester).

One-offs:

```bash
docker-compose run inkshop pt
```

Development:

```bash
docker-compose run inkshop pt --autoreload
```



## Opinionated, and built on:
- [Simple Crypt](https://pypi.org/project/simple-crypt/) (and [pycrypto](https://pypi.org/project/pycrypto/)) for encryption.
- Cloudflare for DNS, Caching, and Development redirects
- Mailgun for email sending.
- AWS S3 for uploads and static file serving.
- Postgres for database.
- Redis for caching and queuing.
- Docker for encapsulation and dev ease.
- Heroku for deployment.



## Current working list

- [ ] get test harness in
- [ ] basic tests passing including flake
- [ ] create subscribe test
- [ ] create functions
- [ ] create message model tests
- [ ] create message model functions, including rendering
- [ ] create scheduledmessage model tests, including timing and tombstoning, and never double-sending.
- [ ] create scheduledmessage model methods
- [ ] create tombstoning model methods
- [ ] create unsubscribe test
- [ ] create functions
- [ ] create love click tests for user and system (mark out unsub)
- [ ] create love click methods
- [ ] create tests that only emails to the right list send. (so when I import, it doesn't accdentally send)
- [ ] create message editing UI
- [ ] create message editing tests
- [ ] message editing tests pass

- [ ] deploy to production
- [ ] make fake list of me
- [ ] send test message to me on production
- [ ] create import CSV support tests
- [ ] create import CSV support method


- [ ] export final list from op
- [ ] import list into production
- [ ] schedule letter for sunday


