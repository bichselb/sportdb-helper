# all commands involving docker use sudo, which is typically required to use docker commands

IMAGE := sportdb-helper
CONTAINER := sportdb-helper-container

# build the docker image
.PHONY: image
image:
	sudo docker build -t $(IMAGE) .


# remove the created docker container
.PHONY: clean
clean:
	sudo docker rm  -f $(CONTAINER) 2>/dev/null || true
	sudo docker rmi -f $(IMAGE)     2>/dev/null || true


.PHONY: run
run: image
	sudo docker run \
		--rm \
		--name $(CONTAINER) \
		--entrypoint "/bin/bash" \
		-it \
		$(IMAGE)


.PHONY: vnc
vnc:
	vncviewer 127.0.0.1:5901
