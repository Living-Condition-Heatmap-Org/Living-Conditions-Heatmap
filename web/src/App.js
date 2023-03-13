import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import * as turf from '@turf/turf'
import { useGoogleLogin, googleLogout} from '@react-oauth/google';
import axios from 'axios';

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

const colorRamp = ["#feebe2", "#fcc5c0", "#fa9fb5", "#f768a1", "#dd3497", "#ae017e", "#7a0177"]

function findCenter(loc) {
    const x = (loc[0][0] + loc[1][0] + loc[2][0] + loc[3][0]) / 4;
    const y = (loc[0][1] + loc[1][1] + loc[2][1] + loc[3][1]) / 4;
    return [x, y];
}


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


    const updateHeatmap = () => {

        const data_json = defaultScores;

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

            let val_walk = data_json[i]['walkScore'];
            let val_bike = data_json[i]['bikeScore'];
            let val_transit = data_json[i]['transitScore'];
            let val_sound = data_json[i]['soundScore'];

            let val = val_walk * sliderWalkWeight
                + val_bike * sliderBikeWeight
                + val_transit * sliderTransitWeight
                + val_sound * sliderSoundWeight;
            
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

        var cellSide = 0.5;
        var grid = turf.squareGrid([bounds.SW.lng, bounds.SW.lat, bounds.NE.lng, bounds.NE.lat], cellSide, 'kilometers');

        for (let i = 0; i < grid.features.length; i++) {
            grid.features[i].properties.highlighted = 'No';
            grid.features[i].properties.id = i;

            const [lng, lat] = findCenter(grid.features[i].geometry.coordinates[0]);

            grid.features[i].properties.lat = lat;
            grid.features[i].properties.lng = lng;

            const lng_idx = Math.floor((lng - bounds.NE.lng) / (bounds.SW.lng - bounds.NE.lng) * grid_array.length);
            const lat_idx = Math.floor((lat - bounds.SW.lat) / (bounds.NE.lat - bounds.SW.lat) * grid_array.length);

            const heatmap_val = ((grid_array[lat_idx][lng_idx] - heatmap_bounds.min) / (heatmap_bounds.max - heatmap_bounds.min) * 5)
            grid.features[i].properties.bin = heatmap_val;
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

    useEffect(() => {
        if (!defaultScores) return;
        const grid = updateHeatmap();
        map.current.getSource('grid-source').setData(grid);
    }, [sliderWalkWeight, sliderBikeWeight, sliderTransitWeight, sliderSoundWeight]);


    const login = useGoogleLogin({
        onSuccess: (codeResponse) => setUser(codeResponse),
        onError: (error) => console.log('Login Failed:', error)
    });

    // Request user meta data upon successfull login.
    useEffect(
        () => {
            if (user) {
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
        if (profile) return <Button variant="contained" onClick={logOut}>Log out</Button>
        else return <Button variant="contained" onClick={() => login()}>Log in</Button>
    }


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
                                Walk Score Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderWalkWeight(v)} defaultValue={100}/>
                            <Typography color="common.white" variant="body2">
                                Bike Score Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderBikeWeight(v)}/>
                            <Typography color="common.white" variant="body2">
                                Transit Score Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderTransitWeight(v)}/>
                            <Typography color="common.white" variant="body2">
                                Sound Score Weight
                            </Typography>
                            <Slider onChangeCommitted={(_, v) => setSliderSoundWeight(v)}/>
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