"use client"
import React, {useEffect, useState} from 'react';
import {LayerGroup, useMap} from 'react-leaflet';
import {ObjectMarker} from "./ObjectMarker";

const DEMO_DATA = [
    {
        "type": "feature",
        "geometry": {
            "type": "Point",
            "coordinates": [41.69462, -8.84679]
        },
        "properties": {
            id: "",
            operator: "",
            date: "",
            fatalities: "",
            imgUrl: "https://cdn-icons-png.flaticon.com/512/1830/1830404.png",
        }
    },

];

function ObjectMarkersGroup() {

    const map = useMap();
    const [geom, setGeom] = useState([...DEMO_DATA]);
    const [bounds, setBounds] = useState(map.getBounds());

    /**
     * Setup the event to update the bounds automatically
     */
    useEffect(() => {
        const cb = () => {
            setBounds(map.getBounds());
        }
        map.on('moveend', cb);

        return () => {
            map.off('moveend', cb);
        }
    }, []);

    /* Updates the data for the current bounds */
    useEffect(() => {
        console.log(`> getting data for bounds`, bounds);
        setGeom(DEMO_DATA);
    }, [bounds])

    return (
        <LayerGroup>
            {
                geom.map(geoJSON => <ObjectMarker key={geoJSON.properties.id} geoJSON={geoJSON}/>)
            }
        </LayerGroup>
    );
}

export default ObjectMarkersGroup;
