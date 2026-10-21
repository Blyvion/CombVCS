<template>
  <v-app id="inspire">
    <v-app-bar
      app
      color="white"
      flat
    >
      <v-container class="py-0 fill-height">
        <v-img
          alt="Vuetify Logo"
          class="shrink mr-2"
          contain
          src="../assets/logo.png"
          transition="scale-transition"
          width="40"
        />
        <v-btn
          href="/"
          text
        >
          Videos
        </v-btn>

        <v-spacer></v-spacer>
      </v-container>
    </v-app-bar>

    <v-main class="grey lighten-3 pt-4">
      <v-container>
        <v-row>
          <v-col cols="2">
            <v-sheet rounded="xlg">
              <v-card-title>
                My Videos
              </v-card-title>
              <v-list color="transparent">
                <div v-if="saved_videos.length > 0">
                  <v-list-item
                    v-for="n,index in saved_videos"
                    :key="n"
                    link
                  >
                    <v-list-item-content @click="viewVideo(index)">
                      <v-list-item-title>
                        <div>
                          {{ crimpFileName(n) }}
                        </div>
                      </v-list-item-title>
                    </v-list-item-content>
                    <v-list-item-action>
                      <v-progress-circular
                          size="40"
                          color="blue"
                          v-if="saved_videos_prog[index] < 100 && saved_videos_state[index] == 'inp'"
                          @mouseenter="active_delete = index"
                          @mouseleave="active_delete = -1"
                        >
                        <v-btn icon @click="deleteInProgressVideo(index);" v-if="active_delete == index">
                          <v-icon>
                            mdi-close-circle
                          </v-icon>
                        </v-btn>
                        <div v-else>
                          {{ saved_videos_prog[index] }}
                        </div>
                      </v-progress-circular>
                      <v-progress-circular
                          indeterminate
                          size="40"
                          color="blue"
                          v-else-if="saved_videos_state[index] == 'wtg'"
                          @mouseenter="active_delete = index"
                          @mouseleave="active_delete = -1"
                        >
                        <v-btn icon @click="deleteInProgressVideo(index);" v-if="active_delete == index">
                          <v-icon>
                            mdi-close-circle
                          </v-icon>
                        </v-btn>
                        <div v-else>
                          ...
                        </div>
                      </v-progress-circular>

                      <v-btn icon @click="deleteVideo(index)" v-else-if="saved_videos_prog[index] == 100">
                        <v-icon>
                          mdi-trash-can-outline
                        </v-icon>
                      </v-btn>
                    </v-list-item-action>
                  </v-list-item>
                </div>
                <div v-else>
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-title class="grey--text">
                        Your saved videos will go here!
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </div>
              </v-list>
            </v-sheet>
          </v-col>

          <v-col>
            <v-sheet
              min-height="70vh"
              rounded="lg"

            >
              <VideoUploader :ip="ip" v-if="showVideo == null" @video_upload_start="updateBusy(true)" @video_upload_finish="addVideo" @not_busy="updateBusy(false)" v-bind:saved_videos="this.saved_videos"/>
              <VideoViewer :ip="ip" v-bind:Video="showVideo" v-else />
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import axios from 'axios'
import VideoUploader from './VideoUploader';
import VideoViewer from './VideoViewer';
import axiosApi from '../utils/axios-instance';

  export default {
    name: 'VideoPanel',

    components: {
      VideoUploader,
      VideoViewer,
    },
    props: {
      ip: String,
    },
    data() {
      return {
        buttons: [
          {label: 'Videos'},
          {link: 'Account'}
        ],
        active_delete: -1,
        showVideo: null,
        saved_videos: [],
        saved_videos_state: [],
        save_videos_prog: [],
      }
    },
    watch:{
      video(){
        this.uploadVideo();
      }
    },
    created(){
      this.loadVideos();
    },
    methods: {
      updateBusy(busy){
        if(busy){
          console.log("SET BUSY");
          this.$emit("busy");
        }else{
          console.log("SET NOT BUSY");
          this.$emit("notbusy");
        }
      },
      viewVideo(index){
        this.showVideo = this.saved_videos[index];
      },
      addVideo(video) {
        console.log("DELETE BEFORE: " + this.active_delete);
        if (video.length > 0) {
          this.saved_videos.push(video);
          this.getProgLevels();
        }
        console.log("DELETE AFTER: " + this.active_delete);
        // this.updateBusy(false);
      },
      deleteInProgressVideo(index){
        this.deleteVideo(index).then(() => {this.active_delete = -1});
      },
      deleteVideo(index){
        return axios.post(
          `http://${this.ip}:32001/deletevideo`,
          this.saved_videos[index],
          {
            headers: { "Content-Type": "text/plain" }
          }
        )
        .then((response) => {
          console.log(response);
          this.loadVideos();
        })
      },
      loadVideos(){
        this.saved_videos = []
        this.saved_videos_prog = []
        this.getSavedVideos().then(() => {
          this.getProgLevels();
        });
      },
      getSavedVideos(){
        // return axios.get(
        //   'http://127.0.0.1:5000/listvideos',
        // )
        // .then((response) => {
        //   this.saved_videos = response.data.videolist;
        // })
        return axiosApi({
          url: '/listvideos',
          method: 'GET',
        }).then((response) => {
          this.saved_videos = response.data.videolist;
        }).catch((error) => {
          console.log(error);
        })
      },
      getProgLevels(){
        this.saved_videos.forEach( () => {
          //Make some call to API for prog levels, for now just setting to 25% for testing
          this.saved_videos_state.push("fin");
          this.saved_videos_prog.push(100);
        });

        // this.saved_videos_state[0] = "inp"
        this.loadingVideos = false;
      },
      crimpFileName(filename){
        var i = filename.lastIndexOf(".");
        var ext = filename.substring(i);
        if(filename.length > 18){
          filename = filename.substring(0,11) + "..." + filename.substring(i-6,i) + ext;
        }
        return filename;
      }
    }
  }
</script>
