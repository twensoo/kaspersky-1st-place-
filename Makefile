all: prepare build run delay5s test

delay5s:
	# can be used to let components start working
	sleep 20

sys-packages:
	sudo apt install -y docker-compose
	sudo apt install python3-pip -y
	sudo pip3 install pipenv

pipenv:
	pipenv install -r requirements-dev.txt	

prepare: clean sys-packages pipenv build

build:
	docker-compose build

run:
	docker-compose up -d

restart:
	docker-compose restart

run-plc:
	pipenv run python plc/plc.py

run-scada:
	pipenv run python scada/scada.py

run-sensors:
	export FLASK_DEBUG=1; pipenv run python sensors/sensors.py

run-license:
	pipenv run python license_server/license_server.py

test:
	docker exec tests py.test


clean:
	docker-compose down; pipenv --rm; rm -rf Pipfile*; echo cleanup complete