<template>
  <v-app>
    <v-overlay v-model="busy" z-index="999">
        <h2>Video Processing - Please Wait</h2>
        <v-progress-linear indeterminate size="200"></v-progress-linear>
    </v-overlay>
    <v-app-bar
      app
      color="primary"
      dark
    >
      <div class="d-flex align-center">
        <v-img
          alt="Vuetify Logo"
          class="shrink mr-2"
          contain
          src="./assets/logo.png"
          transition="scale-transition"
          width="40"
        />

        <v-img
          alt="Vuetify Name"
          class="shrink mt-1 hidden-sm-and-down"
          contain
          min-width="100"
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-name-dark.png"
          width="100"
        />
      </div>

      <v-spacer></v-spacer>

      <v-btn
        href="https://github.com/vuetifyjs/vuetify/releases/latest"
        target="_blank"
        text
      >
        <span class="mr-2">Latest Release</span>
        <v-icon>mdi-open-in-new</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <VideoPanel :ip="ip" @busy="busy = true" @notbusy="busy = false"/>
    </v-main>
  </v-app>
</template>

<script>
import VideoPanel from './components/VideoPanel';
  export default {
    name: 'App',

    components: {
      VideoPanel,
    },

    data() {
      return {
        ip: '127.0.0.1',
        busy: false,
      }
    },
    methods: {
      getVideo(text) {
        let tokens = text.split(' ');
        for (let t of tokens) {
          if (this.videoMap.has(t)) {
            return this.videoMap.get(t);
          }
        }
        return 'N/A';
      }
    }
  };
</script>
