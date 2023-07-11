#!/bin/bash

timer () {
    for i in $(seq ${1}); do
        echo -ne "${i}/${1}\r"
        sleep 1
    done
}

if [[ ! -f ./docker-compose.yaml ]]; then
    echo "Test should be run from the project root!"
    exit 1
fi

if [[ ! -f data/sim_file1.xlsx ]]; then
    echo "Simulation data should be present in data folder"
    exit 1
fi

echo "Recreating database..."
rm database/features.db && sqlite3 database/features.db "VACUUM;"

echo "Preparing Compose cluster..."
docker compose build
docker compose up --force-recreate -d

echo "Sleep for 120 seconds..."
timer 120

echo "Shutting down Compose cluster..."
docker compose down

echo "Checking database tables..."
n_records_table1=$(sqlite3 database/features.db "SELECT COUNT(*) FROM data1;")
n_records_table2=$(sqlite3 database/features.db "SELECT COUNT(*) FROM data2;")
n_records_table3=$(sqlite3 database/features.db "SELECT COUNT(*) FROM data3;")

if [[ "${n_records_table1}" == 50 ]] && [[ "${n_records_table2}" == 50 ]] && [[ "${n_records_table3}" == 50 ]]; then
    echo ✅ Test passed
else
    echo ❌ Test failed. All tables are expected to contain 50 records but 
    echo table1 has ${n_records_table1}
    echo table2 has ${n_records_table2}
    echo table3 has ${n_records_table3}
fi