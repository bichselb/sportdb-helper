FROM selenium/standalone-firefox-debug

USER root

RUN apt-get update && apt-get install -y \
		python3 \
		python3-pip \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*

USER seluser

RUN pip3 install \
	selenium \
	pandas \
	xlrd

# automatically start
RUN mkdir -p /home/seluser/logs
RUN echo "/opt/bin/entry_point.sh > /home/seluser/logs/$(date +%Y-%m-%d_%H-%M-%S).log &" >> /home/seluser/.bashrc

WORKDIR "/sportdb-helper"
COPY --chown=seluser . .
ENTRYPOINT ["python3", "./insert-data.py"]