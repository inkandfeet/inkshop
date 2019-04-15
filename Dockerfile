FROM ubuntu:18.04
MAINTAINER Steven Skoczen <steven@inkandfeet.com>

# Set up the directory for the codebase link.
RUN mkdir -p /inkshop
VOLUME /inkshop

# Update the OS
RUN apt update

# Handle tzdata in non-interative mode.
RUN export DEBIAN_FRONTEND=noninteractive; apt install -y tzdata; ln -fs /usr/share/zoneinfo/UTC /etc/localtime; dpkg-reconfigure --frontend noninteractive tzdata

# Install the base languages & tools
RUN apt install -y curl git nginx python3 python3-pip npm python3-setuptools libpq-dev python3-dev libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev postgresql python-tk libmemcached-dev nodejs libncurses5-dev libffi-dev nano

# Install node globals, pip
RUN pip3 install --upgrade pip
 
# Prep the app for updating.
WORKDIR /inkshop

# Set up reqs
ADD requirements.unstable.txt /inkshop/requirements.unstable.txt
ADD requirements.txt /inkshop/requirements.txt
RUN pip3 install -r requirements.unstable.txt && pip freeze -r requirements.unstable.txt > requirements.txt

# Add less and NPM packages.
ADD package.json /inkshop/package.json
RUN npm i -g less

# Add procfile (via honcho)
ADD Procfile /inkshop/Procfile
ADD Procfile.dev /inkshop/Procfile.dev

# For polytester
ADD tests.yml /inkshop/tests.yml

WORKDIR /inkshop
EXPOSE 8120
