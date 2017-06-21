# Vertogas-Token-Application

## Prerequisites
  - Run on a Linux distribution (ideally Ubuntu 16.04)
  - Have git installed
   - Have the 3 .pickle data files
     - power_plants.pickle
     - biomass.pickle
     - mixes.pickle

     Data are available from [WeTransfer link](https://we.tl/s1dP1sopqn) (last updated 2017-06-21 11:30am / 1 week activity)

## Clone Project
```bash
 $ git clone https://github.com/nicolas-maurice/vertogas-api.git
 $ cd vertogas-api
```

## Setup environment

### Install docker and docker-compose
 ```bash
 $ sudo sh setup-utils/install_docker.sh
 ```
You can restart your computer to ensure everything is set correctly

### Deploy Traefik and Portainer
```bash
$ docker-compose -f setup-utils/docker-compose.dev.yml up -d
```


## Get up and running

### Save data files in the correct folder
 Create the data folder at the root of the project
 ```bash
 $ mkdir data
 ```
 Put all 3 .pickle files (power_plants.pickle, biomass.pickle, mixes.pickle) in ```data/``` folder.


### Deploy the app
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Test API is running correctly
From a Google Chrome browser request the nex URL:
 http://api.localhost/vertogas/tokens/owner/0x13377b14b615fff59c8e66288c32365d38181cdb


 ## About the API

 The base url of the api is ```http://api.localhost``` and 3 routes are available.

 **1. /vertogas/powerPlants/<string:owner>**
  - Method : **GET**
  - Return: list of power plants owned by ```owner```
  (including list of tokens that have been produced by power plants) under format

 ```javascript
 {
     powerPlants: [
         {
             id: Number,
             meta_data: String,
             mix: [
                 {
                     biomass: {
                        id: Number
                        name: String
                     }
                     ratio: Number
                 },
             ]
             name: String,
             owner: string,
             tokens: [
                 {
                     certifID: String,
                     claimer: String,
                     isClaimed: Boolean,
                     metaData: String,
                     owner: String
                 }
             ]
         },
     ],
 }
 ```
  - Addresses of power plants owners :
    - 0x13377b14b615fff59c8e66288c32365d38181cdb

 **2. /vertogas/tokens or /vertogas/tokens/owner/<string:owner> or /vertogas/tokens/powerPlant/<int:power_plant_id>**
  - method : **GET**
  - Return the list of tokens respectevely full list, owned by owner, produced at power_plant_id

 ```javascript
 {
     tokens: [
         {
             certifID: String,
             claimer: String,
             isClaimed: Boolean,
             metaData: String,
             owner: String
         }
     ]
 }
 ```
 - Addresses of token owners:
   - 0x13377b14b615fff59c8e66288c32365d38181cdb
   - 0x00156c662d7dd3049fb7c9667a562b1b51cf1b1b
   - 0x009ad28a153c7dc690ac3337d57ae99a4d73e3cf

 - Available power plant ids: 0 to 6

  **3. /vertogas/logs/<int:token_id>**
   - method : **GET**
   - Return the list of logs concerning token ```token_id```

  ```javascript
  {
      logs: [
          {
              args: Object,
              blockNumber: Number,
              event: {
                  id: Number,
                  name: String,
              }
              timestamp: Date,
          }
      ]
  }
