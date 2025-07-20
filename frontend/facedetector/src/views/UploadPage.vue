<template>
  <div class="upload-page">
    <h1>Распознавание лиц на видео</h1>
    <p>Загрузите видео в формате MP4 (до 1 ГБ)</p>
    <FileDropzone @file-selected="handleFileSelected" />
  </div>
</template>

<script>
import FileDropzone from '../components/FileDropzone.vue'

export default {
  name: 'UploadPage',
  components: { FileDropzone },
  methods: {
    handleFileSelected(file) {
      this.$router.push({ name: 'Processing', params: { file } })
    }
  }
}
</script>

<style scoped>
.upload-page {
  max-width: 600px;
  margin: 0 auto;
}
</style>