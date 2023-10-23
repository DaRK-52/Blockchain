#! /bin/bash

for port in {8081..8089}
	do
		python3.9 app/ssle_app.py -a 127.0.0.1 -p $port &
		sleep 1
	done
