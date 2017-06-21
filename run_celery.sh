sleep 6

vertogas init_db

vertogas insert_contract --address 0xfC12342Dcf4dc690e03325Cc549c1272EA342092 --abi solidity/0xfC12342Dcf4dc690e03325Cc549c1272EA342092/VertogasRegistrar.json
vertogas insert_data -p data/biomass.pickle -p data/power_plants.pickle -p data/mixes.pickle
celery worker -A app --loglevel=INFO -n vertogas1@%h --beat
