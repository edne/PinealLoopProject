#!/bin/sh
set -e

# scripts/build.sh
cp -f src/client.py bin/  # client.py is not preprocessed

export SERVER_ADDR=localhost:7172
export LISTEN_PORT=7173

touch .pineal_history

bin/pineal &

python src/client.py test $(ls examples/*.pn) || echo "TEST FAILED"
