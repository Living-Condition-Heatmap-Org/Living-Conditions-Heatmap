# Living-Conditions-Heatmap
CSE 210 Team 5 project

## Set up conda enviroment:
```
conda create --name heatmap python=3
conda activate heatmap
pip install -r requirements.txt
```

## To run the server:
```
python3 living_condition_heatmap/manage.py runserver 127.0.0.1:8000
```

## Running React Web Applicaiton locally
Place `.env` inside `/web`.
```
cd web
npm install
npm start
```

## Running Swagger for Local Mock APIs
You need Docker Desktop for this.
```
docker run --rm -it -p 3001:4010 -v ${PWD}:/tmp -P stoplight/prism:4 mock -h 0.0.0.0 --cors /tmp/docs/openapi.yaml
```

## Populating the database with locations and their desirability scores (make sure you are in the `heatmap` conda env)
```
cd living_condition_heatmap
python3 populate_json.py <path to Chris's JSON data> <path to env file containing WS and HL API keys>
```
