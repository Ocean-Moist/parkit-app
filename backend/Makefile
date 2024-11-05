# Variables
DOCKER_IMAGE := localhost:5000/oceanmoist/parkit
K8S_DEPLOYMENT := k8s/deployment.yml
K8S_NAMESPACE := parkit

# Default target
all: version build deploy

# Determine the next version based on the previous version
version:
	@echo "Determining the next version..."; \
	PREV_VERSION=$$(cat version.txt | cut -d'=' -f2); \
	if echo $$PREV_VERSION | grep -qP '^\d+\.\d+\.\d+$$'; then \
		MAJOR=$$(echo $$PREV_VERSION | cut -d'.' -f1); \
		MINOR=$$(echo $$PREV_VERSION | cut -d'.' -f2); \
		PATCH=$$(echo $$PREV_VERSION | cut -d'.' -f3); \
		PATCH=$$(expr $$PATCH + 1); \
		echo "$$TEST"; \
		VERSION=$${MAJOR}.$${MINOR}.$${PATCH}; \
	else \
		echo "Previous version ($$PREV_VERSION) doesn't match the expected format. Starting from version 1.0.0"; \
		VERSION=1.0.0; \
	fi; \
	echo "Next version: $$VERSION"; \
	echo "VERSION=$$VERSION" > version.txt


build: version
	VERSION=$$(cat version.txt | cut -d'=' -f2); \
	echo $(DOCKER_IMAGE):$$VERSION; \
	eval $$(minikube docker-env) && \
	docker build -t $(DOCKER_IMAGE):$$VERSION . && \
	docker push $(DOCKER_IMAGE):$$VERSION

# Update the deployment manifest and apply it to Minikube
deploy:
	VERSION=$$(cat version.txt | cut -d'=' -f2); \
	sed -i 's|image: $(DOCKER_IMAGE):.*|image: $(DOCKER_IMAGE):'$$VERSION'|' $(K8S_DEPLOYMENT); \
	kubectl apply -f $(K8S_DEPLOYMENT) -n $(K8S_NAMESPACE)

# Clean up the generated artifacts
clean:
	VERSION=$$(cat version.txt | cut -d'=' -f2); \
	docker rmi $(DOCKER_IMAGE):$$VERSION; \
	git checkout -- $(K8S_DEPLOYMENT); \
	rm -f version.txt


# start minikube, docker on open-rc, open dashboard, and start local docker registry
start:
	doas rc-service docker start
	minikube start
	eval $$(minikube docker-env) && \
	docker run -d -p 5000:5000 --restart=always --name local-registry registry:2

start2:
	doas sysctl -w net.ipv4.conf.all.route_localnet=1
	doas iptables -t nat -A OUTPUT -p tcp --dport 31589 -j DNAT --to-destination $(shell minikube ip):31589
	doas iptables -t nat -A POSTROUTING -j MASQUERADE
	nohup minikube dashboard &

.PHONY: all version build deploy clean