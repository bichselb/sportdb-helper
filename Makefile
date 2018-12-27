# all commands involving docker use sudo, which is typically required to use docker commands

IMAGE := bichselb/sportdb-helper
CONTAINER := sportdb-helper-container
TAG := latest

ROOTDIR := $$(pwd)
RUN := sudo docker run \
		-it \
		--name $(CONTAINER) \
		--workdir="/sportdp-helper" \
		-v $(ROOTDIR):/sportdp-helper \
		$(IMAGE)


# launch a docker container using the image, which will provide a shell in the container
.PHONY: run
run: 
	cd docker && make image clean-container
	$(RUN) python3 insert-data.py

all: run
