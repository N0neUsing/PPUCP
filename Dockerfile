FROM registry.manadrdev.com/ubuntu

MAINTAINER Jason Lu <jason.lu@manadr.com>
RUN	apt-get update && \
	apt-get install -y --allow-unauthenticated \
	curl \
	git \
	wget \
	python \
	python-dev \
	python-setuptools \
	build-essential \
	libssl-dev \
	libffi-dev \
	ruby
RUN easy_install pip
RUN pip install --upgrade pip
RUN gem install tiller
COPY tiller/ /etc/tiller
ADD apps.conf.example /etc/tiller/templates/apps.erb
WORKDIR /usr/local/attendance
COPY requirements.txt ./
RUN pip install -r requirements.txt
ENV DEBUG true
ADD . ./
ADD entrypoint.sh /tmp/entrypoint.sh
RUN chmod a+x /tmp/entrypoint.sh
RUN mkdir /var/log/attendance
CMD ["/usr/local/bin/tiller" , "-v"]
HEALTHCHECK --interval=60s --timeout=30s \
  CMD curl -f http://localhost:5000/fetch -H 'accept: application/json' || exit 1
EXPOSE 5000