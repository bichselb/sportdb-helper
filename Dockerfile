FROM selenium/standalone-firefox-debug

USER root

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
		python3 \
		python3-pip \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*


RUN pip3 install \
	selenium \
	pandas \
	xlrd

WORKDIR "/sportdb-helper"
COPY . .
ENTRYPOINT ["python3", "./insert-data.py"]