"use client"
import React from 'react';
import {MapContainer, TileLayer} from 'react-leaflet';
import ObjectMarkersGroup from "./ObjectMarkersGroup";

function Page() {
    return (
        <MapContainer style={{width: "100%", height: "calc(100vh - 64px)"}}
                      center={[35.00000, 19.99999]}
                      zoom={17}
                      scrollWheelZoom={false}
        >
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <ObjectMarkersGroup/>
        </MapContainer>
    );
}

export default Page;
