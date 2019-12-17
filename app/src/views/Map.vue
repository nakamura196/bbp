<template>
  <div>
    <v-container>
      <div style="width : 100%; height : 600px" class="my-5">
        <v-map :zoom="zoom" :center="center">
          <v-icondefault></v-icondefault>
          <v-tilelayer url="http://{s}.tile.osm.org/{z}/{x}/{y}.png"></v-tilelayer>
          <v-marker-cluster>
            <v-marker
              v-for="(marker, index) in markers"
              v-bind:key="index"
              :lat-lng="marker.latlng"
              :icon="icon"
            >
              <v-popup>
                <a :href="marker.url" target="_blank">{{marker.content}}</a>
              </v-popup>
            </v-marker>
          </v-marker-cluster>
        </v-map>
      </div>

      <br/>

      <p class="mt-5"><code>{{query}}</code></p>
    </v-container>
  </div>
</template>

<script>
import * as Vue2Leaflet from "vue2-leaflet";
import { Icon, icon } from "leaflet";
import Vue2LeafletMarkerCluster from "vue2-leaflet-markercluster";

import iconUrl from "leaflet/dist/images/marker-icon.png";
import shadowUrl from "leaflet/dist/images/marker-shadow.png";

//おまじない
//https://korigan.github.io/Vue2Leaflet/#/quickstart?id=system-wide-components
delete Icon.Default.prototype._getIconUrl;

Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png")
});

export default {
  data: () => ({
    results: [],
    page: 1,
    size: 20,

    query: "",

    //Map
    zoom: 2,
    center: [0, 0],
    url: "http://{s}.tile.osm.org/{z}/{x}/{y}.png",
    attribution:
      '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    markers: [],
    icon: icon(
      Object.assign({}, Icon.Default.prototype.options, { iconUrl, shadowUrl })
    )
  }),
  components: {
    "v-map": Vue2Leaflet.LMap,
    "v-tilelayer": Vue2Leaflet.LTileLayer,
    "v-icondefault": Vue2Leaflet.LIconDefault,
    "v-marker": Vue2Leaflet.LMarker,
    "v-popup": Vue2Leaflet.LPopup,
    "v-marker-cluster": Vue2LeafletMarkerCluster
  },
  mounted() {
    class SPARQLQueryDispatcher {
      constructor(endpoint) {
        this.endpoint = endpoint;
      }

      query(sparqlQuery) {
        const fullUrl =
          this.endpoint + "?query=" + encodeURIComponent(sparqlQuery);
        const headers = { Accept: "application/sparql-results+json" };

        return fetch(fullUrl, { headers }).then(body => body.json());
      }
    }

    const endpointUrl = "https://dbpedia.org/sparql/";

    const sparqlQuery = `
      select distinct * 
      where { 
        ?s <http://dbpedia.org/ontology/industry> dbr:Alcoholic_beverage . 
        ?s geo:lat ?lat . 
        ?s geo:long ?long . 
        ?s rdfs:label ?label . 
        filter(lang(?label) = "en") .
        ?url foaf:primaryTopic ?s
      }
  `;

    this.query = sparqlQuery;

    const queryDispatcher = new SPARQLQueryDispatcher(endpointUrl);
    queryDispatcher.query(sparqlQuery).then(response => {
      let results = response.results.bindings;

      this.markers = [];

      for (let i = 0; i < results.length; i++) {
        let obj = results[i];

        let marker = {
          latlng: [Number(obj.lat.value), Number(obj.long.value)],
          content: obj.label.value,
          url: obj.url.value
        };
        this.markers.push(marker);
      }
    });
  }
};
</script>

<style>
@import "~leaflet/dist/leaflet.css";
@import "~leaflet.markercluster/dist/MarkerCluster.css";
@import "~leaflet.markercluster/dist/MarkerCluster.Default.css";
</style>