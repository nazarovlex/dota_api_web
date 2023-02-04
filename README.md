# dota_api_web

Fill conf.yaml:

- your dota api token: dota_token
- your dota account id: master_id

To prepare project, execute next commands:
- make build

To start project execute:
- make start

After starting the project, you must wait for the parser to complete its work.

To stop project execute:
- make stop

To remove saved data and remove unused docker data:
- make clean

To restart project (clean, build, start):
- make restart
