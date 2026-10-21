<template>
  <div>
    <v-card-title>
      {{this.Video}}
    </v-card-title>
    <search-panel :videoName="Video" @search="refreshIframe" />
    <div class="px-8">
      <iframe id="videoFrame" :src="video" frameborder="0" scrolling="no" width="100%" height="800px"></iframe>
    </div>
  </div>
</template>

<script>
  import SearchPanel from "./SearchPanel.vue";
  export default {
    name: 'VideoViewer',
    components: {
      SearchPanel,
    },
    props: {
      Video: String,
      ip: String,
    },
    data() {
      return {
        video: null,
        frameSwap: true,
      }

    },
    mounted(){
      this.getVideoData();
    },
    watch: {
      Video() {
        this.getVideoData();
      }
    },
    methods: {
      getVideoData(){
        console.log(this.Video);
        this.video = `http://${this.ip}:32001/${this.Video}`;
      },
      refreshIframe() {
        const videoFrame = document.getElementById("videoFrame");
        let src = videoFrame.src + (videoFrame.src.charAt(videoFrame.src.length - 1) === '~' ? '' : '~');
        videoFrame.src = src;
      },
    }
  }
</script>
