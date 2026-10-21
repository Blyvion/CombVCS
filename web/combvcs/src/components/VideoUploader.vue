<template>
  <div>
    <v-card-title>
      Upload a video
    </v-card-title>
    <v-row>
      <v-col cols=1></v-col>
      <v-col>
        <v-file-input
          v-model="video"
          color="deep-purple accent-4"
          counter
          label="Video file input (.mp4)"
          multiple
          placeholder="MP4 Video File"
          prepend-icon="mdi-paperclip"
          outlined
          accept=".mp4"
          :show-size="1000"
        >
          <template v-slot:selection="{ index, text }">
            <v-chip
              v-if="index < 2"
              color="deep-purple accent-4"
              dark
              label
              small
            >
              {{ text }}
            </v-chip>
          </template>
        </v-file-input>
      </v-col>
      <v-col cols=1></v-col>
    </v-row>
    <v-row>
      <v-col cols=1></v-col>
      <v-col class="d-flex justify-center mb-6">
        <v-btn x-large class="primary" @click="uploadVideo">
          Upload your video
        </v-btn>
      </v-col>
      <v-col cols=1></v-col>
    </v-row>
  </div>
</template>

<script>
import axios from 'axios'

  export default {
    name: 'VideoUploader',
    props:{
      saved_videos: Array,
      ip: String,
    },
    data() {
      return {
        links: [
          'Videos',
          'Account'
        ],
        video: null,
        fileTypeError:false,
        duplicateKeyError:false,
      }
    },
    methods: {
      uploadVideo() {
        if (this.video[0] && this.video[0].name.length > 0) {
            var i = this.video[0].name.lastIndexOf(".");
            var ext = this.video[0].name.substring(i);
            if(ext == ".mp4"){
              if(!this.saved_videos.includes(this.video[0].name)){
                this.$emit("video_upload_start");

                //Upload video to server and wait for response and return video name when finished
                this.sendVideo();

                this.$emit("video_upload_finish", this.video[0].name);

                for(i=0; i < 100; i++){
                  setTimeout(() => {this.$emit("loading", i);this.video=null;}, 2000);
                }

                this.video = null;
              }else{
                this.duplicateKeyError=true;
              }
            }else{
              this.video=null;
              this.fileTypeError=true;
            }
        }
      },
      sendVideo() {
        this.$emit("video_upload_start");
        let formData = new FormData();
        formData.append("video", this.video[0]);
        return axios.post(
          `http://${this.ip}:32001/processvideo`,
          formData,
          {
            headers: { "Content-Type": "multipart/form-data" }
          }
        )
        .then((response) => {
          this.$emit("not_busy");
          console.log(response);
        }).catch((error) => {
          this.$emit("not_busy");
          console.log(error);
        })
      },
    }
  }
</script>
