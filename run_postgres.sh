#! /bin/bash

# get directory of current script, regardless of from where it's run
# https://stackoverflow.com/a/246128
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
POSTGRES_DATA_DIR=$DIR/postgres_data
DB_NAME=myclippings

docker run --rm \
    --name mypostgres \
    -e POSTGRES_PASSWORD=mypassword \
    -e POSTGRES_DB=$DB_NAME \
    -v $POSTGRES_DATA_DIR:/var/lib/postgresql/data \
    -p 5432:5432 \
    -d \
    postgres:13.1

