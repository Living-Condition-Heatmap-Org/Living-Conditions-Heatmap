import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import * as turf from '@turf/turf'
import { GoogleLogin } from '@react-oauth/google';
import axios from 'axios';

mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_ACCESS_TOKEN;


function App() {
    const mapContainer = useRef(null);
    const map = useRef(null);
    const [lng, setLng] = useState(-117.2376); // eslint-disable-line no-unused-vars
    const [lat, setLat] = useState(32.8811); // eslint-disable-line no-unused-vars
    const [zoom, setZoom] = useState(13); // eslint-disable-line no-unused-vars
    const [flag, setFlag] = useState(false); // eslint-disable-line no-unused-vars

    // const [getScores, setGetScores] = useState([])

    // useEffect(() => {
    //     axios.get('http://localhost:8000/getScores')
    //     .then(res => {
    //         setGetScores(res.data);
    //         console.log("res.data");
    //         console.log(res.data);
    //     })
    // }, [])

    // const [data, setData] = useState([]);
    // const getData = () => {
    //     fetch('export_dataframe.json', {
    //             headers: {
    //                 'Content-Type': 'application/json',
    //                 'Accept': 'application/json'
    //             }
    //         })
    //         .then(function(response) {
    //             console.log(response)
    //             return response.json();
    //         })
    //         .then(function(myJson) {
    //             console.log(myJson);
    //             setData(myJson);
    //         });
    // }



    useEffect(() => {
        if (map.current) return;
        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: 'mapbox://styles/mapbox/outdoors-v11',
            center: [lng, lat],
            zoom: zoom,
            scrollZoom: true
        });

        const fetchData = async () => {
            // const data = await fetch('export_dataframe.json');
            // const data_json = await data.json();

            const res = await axios.get('http://localhost:8000/getScores');
            const data_json = res.data;
            console.log("data_json");
            console.log(data_json);


            let bounds = { 'NE': { 'lat': 90, 'lng': 180 }, 'SW': { 'lat': -90, 'lng': -180 } }
            for (let i = 0; i < data_json.length; i++) {
                const lat = data_json[i]['latitude'];
                const lng = data_json[i]['longitude'];
                if (lat < bounds.NE.lat) bounds.NE.lat = lat;
                if (lat > bounds.SW.lat) bounds.SW.lat = lat;
                if (lng < bounds.NE.lng) bounds.NE.lng = lng;
                if (lng > bounds.SW.lng) bounds.SW.lng = lng;
            }

            let heatmap_bounds = { 'max': 0, 'min': 1 };
            let grid_map = new Map();
            for (let i = 0; i < data_json.length; i++) {
                const lat = data_json[i]['latitude'];
                const lng = data_json[i]['longitude'];
                const val = data_json[i]['walkScore'];

                if (!grid_map.has(lat)) {
                    grid_map.set(lat, new Map());
                }

                grid_map.get(lat).set(lng, val);

                if (val < heatmap_bounds.min) heatmap_bounds.min = val;
                if (val > heatmap_bounds.max) heatmap_bounds.max = val;
            }
            grid_map = new Map([...grid_map.entries()].sort());

            let idx = 0;
            let grid_array = new Array(grid_map.size);
            for (let [key, value] of grid_map.entries()) {
                const tmp_map = new Map([...value.entries()].sort());
                grid_array[idx] = Array.from(tmp_map.values());
                idx++;
            }

            // 0: SE
            // 24: NW
            const colorRamp = ["#feebe2", "#fcc5c0", "#fa9fb5", "#f768a1", "#dd3497", "#ae017e", "#7a0177"]

            var cellSide = 0.5;
            var grid = turf.squareGrid([bounds.SW.lng, bounds.SW.lat, bounds.NE.lng, bounds.NE.lat], cellSide, 'kilometers');

            for (let i = 0; i < grid.features.length; i++) {
                grid.features[i].properties.highlighted = 'No';
                grid.features[i].properties.id = i;

                const lng = grid.features[i].geometry.coordinates[0][0][0];
                const lat = grid.features[i].geometry.coordinates[0][0][1];

                const lng_idx = Math.floor((lng - bounds.NE.lng) / (bounds.SW.lng - bounds.NE.lng) * grid_array.length);
                const lat_idx = Math.floor((lat - bounds.SW.lat) / (bounds.NE.lat - bounds.SW.lat) * grid_array.length);

                const heatmap_val = ((grid_array[lat_idx][lng_idx] - heatmap_bounds.min) / (heatmap_bounds.max - heatmap_bounds.min) * 5)
                grid.features[i].properties.bin = heatmap_val;
            }

            console.log(`squareGrid - after:`, grid);

            map.current.on('load', () => {
                console.log(`-- Loaded --`);
                map.current.addSource('grid-source', {
                    'type': "geojson",
                    'data': grid,
                    'generateId': true
                });
                map.current.addLayer({
                    'id': 'grid-layer',
                    'type': 'fill',
                    'source': 'grid-source',
                    // 'paint': {
                    //   'fill-outline-color': 'rgba(0,0,0,0.1)',
                    //   'fill-color': 'rgba(0,0,0,0.1)'
                    // }
                    'paint': {
                        'fill-color': {
                            property: 'bin',
                            stops: colorRamp.map((d, i) => [i, d])
                        },
                        'fill-opacity': 0.4
                    }
                });
                map.current.addLayer({
                    'id': 'grid-layer-highlighted',
                    'type': 'fill',
                    'source': 'grid-source',
                    'paint': {
                        'fill-outline-color': '#484896',
                        'fill-color': '#6e599f',
                        'fill-opacity': 0.75
                    },
                    //'filter': ['==', ['get', 'highlighted'], 'Yes']
                    'filter': ['==', ['get', 'id'], -1]
                });


                //click action
                map.current.on('click', 'grid-layer', function(e) {
                    var selectIndex = e.features[0].id;
                    grid.features[e.features[0].id].properties.highlighted = 'Yes';
                    console.log(`highlighted before:`, e.features[0].properties.highlighted);
                    e.features[0].properties.highlighted = 'Yes';
                    console.log(`feature:`, e.features[0]);
                    console.log(`selectIndex:`, selectIndex);
                    console.log(`highlighted after:`, e.features[0].properties.highlighted);

                    const filter = ['==', ['number', ['get', 'id']], selectIndex];

                    map.current.setFilter('grid-layer-highlighted', filter);

                    axios.put("http://localhost:8000/updateRating/", {
                        score: 1,
                        latitude: 32.4324,
                        longitude: -127.3423,
                    });
                });
            });
        }

        fetchData()

        // Clean up on unmount
        return () => map.current.remove();
    }, []);

    useEffect(() => {
        if (!map.current) return; // wait for map to initialize
        map.current.on('move', () => {
            setLng(map.current.getCenter().lng.toFixed(4));
            setLat(map.current.getCenter().lat.toFixed(4));
            setZoom(map.current.getZoom().toFixed(2));
        });
    });

    return (
        <div>
            <div className="sidebar">
            Longitude: {lng} | Latitude: {lat} | Zoom: {zoom} | click : {flag == true}
            </div>
            <div ref={mapContainer} className="map-container" />
            <GoogleLogin
                onSuccess={credentialResponse => {
                console.log(credentialResponse);
                }}
            
                onError={() => {
                console.log('Login Failed');
                }}
                useOneTap
            />
        </div>
    );
}

export default App;