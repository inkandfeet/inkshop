FROM ubuntu:18.04
MAINTAINER Steven Skoczen <steven@inkandfeet.com>

# Set up the directory for the codebase link.
RUN mkdir -p /project
RUN mkdir -p /project/inkshop
VOLUME /project/inkshop

# Update the OS
RUN apt-get update

# Handle tzdata in non-interative mode.
RUN export DEBIAN_FRONTEND=noninteractive; apt-get install -y tzdata; ln -fs /usr/share/zoneinfo/UTC /etc/localtime; dpkg-reconfigure --frontend noninteractive tzdata

# Install the base languages & tools
RUN apt-get install -y curl git nginx python3 python3-pip npm python3-setuptools libpq-dev python3-dev libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev postgresql python-tk libmemcached-dev nodejs libncurses5-dev libffi-dev nano

WORKDIR /project

# Install node globals, pip
RUN pip3 install --upgrade pip
 
# Set up reqs
ADD requirements.unstable.txt /project/requirements.unstable.txt
ADD requirements.txt /project/requirements.txt
RUN pip3 install -r /project/requirements.unstable.txt && pip freeze -r /project/requirements.unstable.txt > /project/requirements.txt

# Add less and NPM packages.
# ADD package.json /project/package.json
RUN npm i -g less

# Add procfile (for honcho)
ADD Procfile /project/Procfile
# pulls beat
ADD Procfile.dev /project/Procfile.dev 
ADD manage.py /project/manage.py

# For polytester
ADD tests.yml /inkshop/tests.yml

EXPOSE 8120
WORKDIR /project
