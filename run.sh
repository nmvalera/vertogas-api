sleep 6

vertogas init_db
vertogas insert_contract --address 0x57a0526fbce4183d146be2ef31e16969dacf51bf --abi solidity/0x57a0526fbce4183d146be2ef31e16969dacf51bf/abi.json
celery worker -A app --loglevel=DEBUG -n vertogas1@%h --beat
gunicorn -w 2 -b :80 run:app
