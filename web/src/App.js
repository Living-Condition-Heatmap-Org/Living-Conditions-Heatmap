import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import * as turf from '@turf/turf'
import { useGoogleLogin, googleLogout} from '@react-oauth/google';
import axios from 'axios';

// Styles using MUI Library
import "normalize.css";
import PropTypes from 'prop-types';
import { Grid, Box } from '@material-ui/core';
import { createTheme, ThemeProvider } from "@material-ui/core/styles";
import { Stack, Slider, Typography, Button, Rating } from '@mui/material';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';

import Header from './components/Header';

mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_ACCESS_TOKEN;

const theme = createTheme({
    typography: {
        fontSize: 24,
    },
    palette: {
        primary: {
            main: "#182B49"
        },
        secondary: {
            main: "#ffa500"
        }
    }
});

// Color map for the heatmap
const colorRamp = ["#feebe2", "#fcc5c0", "#fa9fb5", "#f768a1", "#dd3497", "#ae017e", "#7a0177"]

// Find the center coordinates from 4 corners
function findCenter(loc) {
    const x = (loc[0][0] + loc[1][0] + loc[2][0] + loc[3][0]) / 4;
    const y = (loc[0][1] + loc[1][1] + loc[2][1] + loc[3][1]) / 4;
    return [x, y];
}

// UI and click-events for the rating popup window
function SimpleDialog(props) {
    const { onClose, open, onClick } = props;

    const handleClose = () => {
        onClose();
    };

    return (
        <Dialog onClose={handleClose} open={open}>
        <DialogTitle>How do you rate this location?</DialogTitle>
        <Box sx={{ mb: 2, mt: -1 }}>
            <center>
                <Rating
                    name="simple-controlled"
                    onChange={(event, newValue) => {
                        onClick(newValue);
                    }}
                />
            </center>
        </Box>
        </Dialog>
    );
}

SimpleDialog.propTypes = {
    onClose: PropTypes.func.isRequired,
    open: PropTypes.bool.isRequired,
    onClick: PropTypes.func.isRequired,
};


function App() {
    const mapContainer = useRef(null);
    const map = useRef(null);
    const [lng, setLng] = useState(-117.2376); // eslint-disable-line no-unused-vars
    const [lat, setLat] = useState(32.8811); // eslint-disable-line no-unused-vars
    const [zoom, setZoom] = useState(13); // eslint-disable-line no-unused-vars

    const [ user, setUser ] = useState(null);
    const [ profile, setProfile ] = useState(null);

    const [sliderWalkWeight, setSliderWalkWeight] = useState(100);
    const [sliderBikeWeight, setSliderBikeWeight] = useState(0);
    const [sliderTransitWeight, setSliderTransitWeight] = useState(0);
    const [sliderSoundWeight, setSliderSoundWeight] = useState(0);
    const [sliderGroceryWeight, setSliderGroceryWeight] = useState(0);
    const [sliderSchoolWeight, setSliderSchoolWeight] = useState(0);
    const [sliderStopWeight, setSliderStopWeight] = useState(0);


    const [ defaultScores, setDefaultScores ] = useState(null);
    const getScores = async () => {
        axios.get('http://localhost:8000/getScores').then(response => {
            setDefaultScores(response.data);
        });
    }

    const [ userRatings, setUserRatings ] = useState(null);
    const getUserRatings = async () => {
        axios.get('http://localhost:8000/getRating/').then(response => {
            setUserRatings(response.data);
            console.log(response.data);
        });
    }

    const [ userRecommendation, setUserRecommendation ] = useState(null);
    const getRecommendation = async () => {
        axios.get('http://localhost:8000/getRecommendation/').then(response => {
            setUserRecommendation(response.data);
            console.log(response.data);
        });
    }

    // Popup window for rating
    const [open, setOpen] = React.useState(false);
    const [uiRatingValue, setUiRatingValue] = React.useState(2);
    const [uiRatingLat, setUiRatingLat] = useState(null);
    const [uiRatingLng, setUiRatingLng] = useState(null);

    // Click event for the opening the popup window.
    const handleClickOpen = (lat, lng) => {
        setOpen(true);
        setUiRatingLat(lat);
        setUiRatingLng(lng);
    };

    // Close event for the popup window.
    const handleClose = () => {
        setOpen(false);

        axios.put("http://localhost:8000/updateRating/", {
            score: uiRatingValue,
            latitude: uiRatingLat,
            longitude: uiRatingLng,
        });
    };

    // Click event for the star rating on the popup window.
    const handleClick = (value) => {
        setUiRatingValue(value);
    };


    // Returns the grid object that can be used for updating the heatmap; no side effect.
    const updateHeatmap = () => {

        const data = defaultScores;

        // Find the bounds of the heatmap.
        // North East: Smallest latitude, largest longitude
        // South West: Largest latitude, smallest longitude
        let bounds = { 'min': { 'lat': 90, 'lng': 180 }, 'max': { 'lat': -90, 'lng': -180 } }
        for (let i = 0; i < data.length; i++) {
            const lat = data[i]['latitude'];
            const lng = data[i]['longitude'];
            if (lat < bounds.min.lat) bounds.min.lat = lat;
            if (lat > bounds.max.lat) bounds.max.lat = lat;
            if (lng < bounds.min.lng) bounds.min.lng = lng;
            if (lng > bounds.max.lng) bounds.max.lng = lng;
        }

        // console.log("bounds", bounds);

        let property_ranges = {
            'walkScore': {'max':0, 'min':100},
            'bikeScore': {'max':0, 'min':100},
            'transitScore': {'max':0, 'min':100},
            'soundScore': {'max':0, 'min':100},
            'nearestGrocery': {'max':0, 'min':100},
            'nearestSchool': {'max':0, 'min':100},
            'nearestTransit': {'max':0, 'min':100}
        }

        // Compute the max and min for each property for normalization
        for (let i = 0; i < data.length; i++) {
            for (let key in property_ranges) {
                if (data[i][key] < property_ranges[key]['min']) property_ranges[key]['min'] = data[i][key];
                if (data[i][key] > property_ranges[key]['max']) property_ranges[key]['max'] = data[i][key];
            }
        }

        let heatmap_bounds = { 'max': 0, 'min': 1 };
        let grid_map = new Map();
        for (let i = 0; i < data.length; i++) {
            const lat = data[i]['latitude'];
            const lng = data[i]['longitude'];

            let val_walk = (data[i]['walkScore'] - property_ranges['walkScore']['min']) / (property_ranges['walkScore']['max'] - property_ranges['walkScore']['min']);
            let val_bike = (data[i]['bikeScore'] - property_ranges['bikeScore']['min']) / (property_ranges['bikeScore']['max'] - property_ranges['bikeScore']['min']);
            let val_transit = (data[i]['transitScore'] - property_ranges['transitScore']['min']) / (property_ranges['transitScore']['max'] - property_ranges['transitScore']['min']);
            let val_sound = (data[i]['soundScore'] - property_ranges['soundScore']['min']) / (property_ranges['soundScore']['max'] - property_ranges['soundScore']['min']);
            let val_grocery = (data[i]['nearestGrocery'] - property_ranges['nearestGrocery']['min']) / (property_ranges['nearestGrocery']['max'] - property_ranges['nearestGrocery']['min']);
            let val_school =(data[i]['nearestSchool'] - property_ranges['nearestSchool']['min']) / (property_ranges['nearestSchool']['max'] - property_ranges['nearestSchool']['min']);
            let val_stop = (data[i]['nearestTransit'] - property_ranges['nearestTransit']['min']) / (property_ranges['nearestTransit']['max'] - property_ranges['nearestTransit']['min']);

            // console.log(val_walk, val_bike, val_transit, val_sound, val_grocery, val_school, val_stop);

            let val = val_walk * sliderWalkWeight / 100.0
                + val_bike * sliderBikeWeight / 100.0
                + val_transit * sliderTransitWeight / 100.0
                + val_sound * sliderSoundWeight / 100.0
                + val_grocery * sliderGroceryWeight / 100.0
                + val_school * sliderSchoolWeight / 100.0
                + val_stop * sliderStopWeight / 100.0;
            
            // console.log(val);
            
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

        const lat_unit = (bounds.max.lat - bounds.min.lat) / 4.;
        const lng_unit = (bounds.max.lng - bounds.min.lng) / 4.;
        // const boundsExtended = bounds;
        const boundsExtended = { 
            'min': { 'lat': bounds.min.lat - lat_unit, 'lng': bounds.min.lng - lng_unit }, 
            'max': { 'lat': bounds.max.lat + lat_unit, 'lng': bounds.max.lng + lng_unit } 
        }


        // console.log("boundsExtended", boundsExtended);

        // 1 degree in latitude is about 111 kilometers.
        let cellSide = lat_unit * 111 / 2;

        var grid = turf.squareGrid([
            boundsExtended.min.lng, 
            boundsExtended.min.lat, 
            boundsExtended.max.lng, 
            boundsExtended.max.lat], cellSide, 'kilometers');

        for (let i = 0; i < grid.features.length; i++) {
            grid.features[i].properties.highlighted = 'No';
            grid.features[i].properties.id = i;

            const [lng, lat] = findCenter(grid.features[i].geometry.coordinates[0]);

            grid.features[i].properties.lat = lat;
            grid.features[i].properties.lng = lng;

            const lng_idx = Math.floor((lng - boundsExtended.min.lng) / (boundsExtended.max.lng - boundsExtended.min.lng) * grid_array.length);
            const lat_idx = Math.floor((lat - boundsExtended.min.lat) / (boundsExtended.max.lat - boundsExtended.min.lat) * grid_array.length);

            const heatmap_val = ((grid_array[lat_idx][lng_idx] - heatmap_bounds.min) / (heatmap_bounds.max - heatmap_bounds.min) * 5);
            grid.features[i].properties.bin = heatmap_val;
            // console.log("heatmap_val", heatmap_val);
        }

        return grid;
    }

    // Initial setup
    useEffect(() => {
        getScores();

        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: 'mapbox://styles/mapbox/outdoors-v11',
            center: [lng, lat],
            zoom: zoom,
            scrollZoom: true
        });
    }, []);

    // Called when scores are downloaded or updated
    useEffect(() => {

        if (!defaultScores) return;
        if (!map.current) return;

        const grid = updateHeatmap();

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
        });

        // Clean up on unmount
        return () => map.current.remove();
    }, [defaultScores]);

    // Update the heatmap when the slider value changes.
    useEffect(() => {
        if (!defaultScores) return;
        const grid = updateHeatmap();
        map.current.getSource('grid-source').setData(grid);
    }, [sliderWalkWeight, sliderBikeWeight, sliderTransitWeight, sliderSoundWeight, sliderGroceryWeight, sliderSchoolWeight, sliderStopWeight]);


    const login = useGoogleLogin({
        onSuccess: (codeResponse) => setUser(codeResponse),
        onError: (error) => console.log('Login Failed:', error)
    });

    // Request user meta data upon successfull login.
    useEffect(
        () => {
            if (user) {
                console.log(user);
                axios
                    .get(`https://www.googleapis.com/oauth2/v1/userinfo?access_token=${user.access_token}`, {
                        headers: {
                            Authorization: `Bearer ${user.access_token}`,
                            Accept: 'application/json'
                        }
                    })
                    .then((res) => {
                        setProfile(res.data);
                    })
                    .catch((err) => console.log(err));

                // Add Google access token for PUT and GET requests from now on.
                axios.defaults.headers.put['Authorization'] = `Bearer ${user.access_token}`;
                axios.defaults.headers.get['Authorization'] = `Bearer ${user.access_token}`;
    
                getUserRatings();

                // Register click event for the rating.
                const grid = updateHeatmap();
                map.current.on('click', 'grid-layer', function(e) {
                    var selectIndex = e.features[0].id;
                    grid.features[e.features[0].id].properties.highlighted = 'Yes';
                    e.features[0].properties.highlighted = 'Yes';

                    const filter = ['==', ['number', ['get', 'id']], selectIndex];

                    map.current.setFilter('grid-layer-highlighted', filter);

                    handleClickOpen(grid.features[e.features[0].id].properties.lat, grid.features[e.features[0].id].properties.lng);
                });
                map.current.getSource('grid-source').setData(grid);

            }
        },
        [ user ]
    );

    const logOut = () => {
        googleLogout();
        setProfile(null);
        setUser(null);
    };

    function LoginComponent() {
        if (profile) {
            return (
                <div>
                    <Button style={{ fontSize: '10px' }} variant="contained" onClick={showRecommendation}>Show AI Recommendation</Button>
                    <br/>
                    <br/>
                    <Button variant="contained" onClick={logOut}>Log out</Button>
                </div>
            )
        }
        else return <Button variant="contained" onClick={() => login()}>Log in</Button>
    }

    const showRecommendation = () => {
        getRecommendation();
    }

    // Show the best recommended location on the map.
    useEffect(() => {
        if (!userRecommendation) return;
        new mapboxgl.Marker()
            .setLngLat([userRecommendation[0]['longitude'], userRecommendation[0]['latitude']])
            .addTo(map.current);
        new mapboxgl.Marker()
            .setLngLat([userRecommendation[1]['longitude'], userRecommendation[1]['latitude']])
            .addTo(map.current);
    }, [userRecommendation]);


    return (
        <ThemeProvider theme={theme}>
            <Box sx={{ flexGrow: 1 }} bgcolor="primary.main">
                <Grid item>
                    <Header />
                </Grid>
                <Grid item container>
                    <Grid item sm={2}>
                        <Stack sx={{ p: 3 }}>
                            <Typography color="common.white" variant="body2">
                                Walkability Score Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderWalkWeight(v)} defaultValue={100}/>
                            <Typography color="common.white" variant="body2">
                                Bike Score Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderBikeWeight(v)}/>
                            <Typography color="common.white" variant="body2">
                                Overall Transit Score Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderTransitWeight(v)}/>
                            <Typography color="common.white" variant="body2">
                                Quietness Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderSoundWeight(v)}/>
                            <Typography color="common.white" variant="body2">
                                Grocery Proximity Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderGroceryWeight(v)}/>
                            <Typography color="common.white" variant="body2">
                                School Proximity Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderSchoolWeight(v)}/>
                            <Typography color="common.white" variant="body2">
                                Transit Proximity Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderStopWeight(v)}/>
                            <br/>
                            <LoginComponent/>
                        </Stack>
                    </Grid>
                    <Grid item sm={10}>
                        <div ref={mapContainer} className="map-container" />
                    </Grid>
                </Grid>
            </Box>
            <SimpleDialog
                open={open}
                onClose={handleClose}
                onClick={handleClick}
            />
        </ThemeProvider>
    );
}

export default App;