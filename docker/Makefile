# all commands involving docker use sudo, which is typically required to use docker commands

IMAGE := bichselb/sportdb-helper
CONTAINER := sportdb-helper-container
TAG := latest

DOCKERDIR := $$(pwd)
ROOTDIR := DOCKERDIR/..
RUN := sudo docker run \
		-it \
		--name $(CONTAINER) \
		--workdir="/sportdp-helper" \
		-v $(ROOTDIR):/sportdp-helper \
		$(IMAGE)

# build the docker image
.PHONY: image
image:
    rsync ../ ./root --exclude=../docker
	sudo docker build -t $(IMAGE):$(TAG) .

# launch a docker container using the image, which will provide a shell in the container
.PHONY: run
run: image clean-container
	$(RUN)

# remove the created docker container
.PHONY: clean-container
clean-container:
	sudo docker rm $(CONTAINER) || true
