<template>
  <div>
    <v-container>
      <v-row>
        
        <v-col cols="12" sm="9">

          <v-row>
            <v-col>
              <h3>
          {{((page - 1) * size + 1).toLocaleString()}} - {{(page * size > total ? total : page * size).toLocaleString()}} of {{total.toLocaleString()}} results
          </h3>
          </v-col>
          <v-col>

            </v-col>
            </v-row>

            

          <template v-if="results.hits">

            <div class="text-center">
            <v-pagination
              v-model="page"
              :length="pagination_length"
              :total-visible="7"
              @input="page_move()"
            ></v-pagination>
          </div>

          <v-card class="my-5" v-for="(obj, i) in results.hits.hits" :key="i">
            <v-row>
              <v-col cols="12" sm="4">
                <v-card-text>
                  <v-img v-if="obj.image" :src="obj.image.value" class="grey lighten-2"></v-img>
                </v-card-text>
              </v-col>
              <v-col cols="12" sm="8">
                <v-card-title>{{obj.label.value}}</v-card-title>
                <v-card-text>
                  <p v-if="obj.inception">
                    <b>Inception:</b>
                    {{obj.inception.value.split("-")[0]}}
                  </p>
                  <p v-if="obj.country">
                    <b>Country:</b>
                    {{obj.country_label.value}}
                  </p>
                  <p v-if="obj.manufacturer">
                    <b>Manufacturer:</b>
                    {{obj.manufacturer_label.value}}
                  </p>
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>

          <div class="text-center">
            <v-pagination
              v-model="page"
              :length="pagination_length"
              :total-visible="7"
              @input="page_move()"
            ></v-pagination>
          </div>

          </template>
        </v-col>
        <v-col cols="12" sm="3">
          <template v-if="results.aggregations">
          <v-card
            class="my-5"
            v-for="(obj, index) in results.aggregations"
            :key="index"
            
          >
            <v-list subheader two-line flat>
              <v-subheader>{{index}}</v-subheader>

              <v-list-item-group multiple>
                <v-list-item v-for="(bucket, index2) in obj.buckets" :key="index2">
                  <template v-slot:default="{ active, toggle }">
                    <v-list-item-action>
                      <v-checkbox v-model="active" color="primary" @click="toggle"></v-checkbox>
                    </v-list-item-action>

                    <v-list-item-content>
                      <v-list-item-title>{{bucket.key}}</v-list-item-title>
                    </v-list-item-content>

                    <v-list-item-action>
                      <v-btn icon>{{bucket.doc_count}}</v-btn>
                    </v-list-item-action>
                  </template>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card>
          </template>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  data: () => ({
    results: [],
    page: 1,
    size: 20
  }),
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

    const endpointUrl = "https://query.wikidata.org/sparql";
    const sparqlQuery = `#ネコ
SELECT DISTINCT *
WHERE 
{
  {  ?item wdt:P31 wd:Q15075508;
        rdfs:label ?label . }
  union {
  ?item wdt:P31 wd:Q44;
        rdfs:label ?label . 
        }
        
  filter(lang(?label) = "en")
  optional { ?item wdt:P18 ?image }
  optional { ?item wdt:P571 ?inception }
   optional { ?item wdt:P495 ?country . ?country rdfs:label ?country_label . filter(lang(?country_label) = "en")}
  optional { ?item wdt:P176 ?manufacturer . ?manufacturer  rdfs:label ?manufacturer_label . filter(lang(?manufacturer_label) = "en") }
}`;

    const queryDispatcher = new SPARQLQueryDispatcher(endpointUrl);
    queryDispatcher.query(sparqlQuery).then(response => {
      let results = response.results.bindings;

      //this.results = results;

      //console.log(response);

      let index = {}
      for(let i = 0; i < results.length; i++){
        let obj = results[i]
        for(let key in obj){
          let value = obj[key].value

          if(key == "inception"){
            value = value.split("-")[0]
          }

          if(!index[key]){
            index[key] = {}
          }
          if(!index[key][value]){
            index[key][value] = 0
          }
          index[key][value] += 1
        }
      }

      let aggs = {};

      let op = [
        {
          label: "Inception",
          field: "inception"
        },
        {
          label: "Country",
          field: "country_label"
        },
        {
          label: "Manufacturer",
          field: "manufacturer_label"
        }
      ];

      let query_aggs = {
      }

      for (let i = 0; i < op.length; i++) {
        let obj = op[i];
        query_aggs[obj.label] = {
          terms: {
            field: obj.field,
            order: {
              _count: "desc"
            },
            size: 20
          }
        };
      }

      for (let label in query_aggs) {
        let obj = query_aggs[label].terms;
        let size = Number(obj.size);
        let field = obj.field.replace(".keyword", "");
        let map = index[field];

        let map_new = {};
        for (let value in map) {
          map_new[value] = map[value];
        }

        //オブジェクトに変換
        let arr = Object.keys(map_new).map(e => ({
          key: e,
          value: map_new[e]
        }));

        //値でそーと
        arr.sort(function(a, b) {
          if (a.value < b.value) return 1;
          if (a.value > b.value) return -1;
          return 0;
        });

        if (size > arr.length) {
          size = arr.length;
        }

        let buckets = [];
        for (let i = 0; i < size; i++) {
          buckets.push({
            key: arr[i].key,
            doc_count: arr[i].value
          });
        }

        aggs[field] = {
          buckets: buckets
        };
      }

      let result = {
        aggregations: aggs,
        hits: {
          hits: results,
          total: {
            relation: "gte",
            value: results.length
          }
        }
      };

      //console.log(result);

      this.results = result;
    });
  },
  computed: {
    // 算出 getter 関数
    total: function() {
      let total = 0;
      if (this.results.hits) {
        total = this.results.hits.total.value;
      }
      return total;
    },
    pagination_length: function() {
      return Math.ceil(this.total / this.size);
    }
  }
};
</script>
