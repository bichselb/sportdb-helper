FROM ubuntu:18.04

#############
# packages #
#############

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
		firefox \
		python3 \
		python3-pip \
		wget \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*

################
# pip packages #
################

RUN pip3 install \
	selenium \
	pandas \
	xlrd

###############
# geckodriver #
###############

# prepare directory
ARG geckodir=/opt/geckodriver
ARG archive=geckodriver.tar.gz

RUN mkdir -p $geckodir && \
        cd $geckodir && \
		wget -O $archive https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz && \
		tar -xvzf $archive && \
		chmod +x geckodriver && \
		ln -s "$geckodir/geckodriver" "/usr/local/bin/geckodriver" && \
		rm -archive


COPY ./root /sportdb-helper

CMD ["./insert-data.py"]