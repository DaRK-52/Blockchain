#! /bin/bash

python3.9 dns_server.py &
sleep 1

for port in {8080..8085}
	do
		python3.9 app/ssle_app.py -a 127.0.0.1 -p $port &
		sleep 1
	done
