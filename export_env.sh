#!/bin/bash

GMOCOIN_API_KEY=""
GMOCOIN_API_SECRET=""

echo -n "API Key: "
read -sr GMOCOIN_API_KEY
echo
echo -n "API Secret: "
read -sr GMOCOIN_API_SECRET

export GMOCOIN_API_KEY
export GMOCOIN_API_SECRET
