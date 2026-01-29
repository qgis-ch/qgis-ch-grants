# QGIS-CH Voting App

## Preparation

* `git clone https://github.com/qgis-ch/qgis-ch-grants.git`
* `cd qgis-ch-grants && mkdir data`
* `cp .env.example .env` and update `.env`
* Build and start the container with `docker compose build` and `docker compose up -d`
* Copy Excelsheet `projekte.template.xlsx` to `data/projekte.xlsx` and update the table
* Write out the env variables to current session `source .env`
* Write the JSON file with projects `docker exec --env-file .env -it qgis-ch-grants-2026 bash -c "python3 /app/xlsx-to-json.py" > data/projekte.json`
* Write the tokens `docker exec --env-file .env -it qgis-ch-grants-${GRANTS_YEAR} bash -c "python3 /app/tokenizer.py" > data/tokens.txt`
* Go to `http://localhost:8501/`
 