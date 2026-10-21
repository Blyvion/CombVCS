const { defineConfig } = require('@vue/cli-service')
const path = require('path');
module.exports = defineConfig({
  transpileDependencies: [
    'vuetify'
  ],
  devServer:{
    static: {
      directory: path.join(__dirname, 'public'),
    },
    compress:true,
    port:8080,
  }
})
