<template>
  <v-app>
    <Header />
    <v-content>
      <router-view />
    </v-content>

    <v-footer :dark="true" :inset="true" class="mt-5">
      <v-container>
        <p class="text-center my-5">
          Beyond Book Project
        </p>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script>
import Header from "@/components/Header";

export default {
  components: {
    Header
  },
  data: () => ({
  }),
  methods: {
    
  }
};
</script>
