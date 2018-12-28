# all commands involving docker use sudo, which is typically required to use docker commands

SELENIUM_CONTAINER := selenium-container

.PHONY: selenium
selenium: clean
	sudo docker run -d \
		-p 4444:4444 \
		-p 5901:5900 \
		-v /dev/shm:/dev/shm \
		-e VNC_NO_PASSWORD=1 \
		--name $(SELENIUM_CONTAINER) \
		selenium/standalone-firefox-debug


IMAGE := sportdb-helper
CONTAINER := sportdb-helper-container

# build the docker image
.PHONY: image
image: clean selenium
	sudo docker build -t $(IMAGE) .


# remove the created docker container
.PHONY: clean
clean:
	sudo docker rm -f $(CONTAINER) || true
	sudo docker rm -f $(SELENIUM_CONTAINER) || true

.PHONY: vnc
vnc:
	vncviewer 127.0.0.1:5901


.PHONY: run
run:
	sudo docker run \
		--name $(CONTAINER) \
		--entrypoint "/bin/bash" \
		-it \
		$(IMAGE)