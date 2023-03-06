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
Obtain Mapbox access key from https://www.mapbox.com/

Add to `src/App.js` `mapboxgl.accessToken = '';`

```
cd web
npm install
npm start
```
