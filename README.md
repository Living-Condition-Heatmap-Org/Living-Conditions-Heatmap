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