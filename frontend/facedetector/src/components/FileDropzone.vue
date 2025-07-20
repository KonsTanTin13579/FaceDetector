<template>
  <div class="dropzone" @dragover.prevent @drop.prevent="handleDrop">
    <input
        type="file"
        accept="video/mp4"
        @change="handleFileChange"
        style="display: none"
        ref="fileInput"
    />
    <button @click="openFileDialog" :disabled="uploading">Выберите файл</button>
    <p>mp4 (до 1 ГБ)</p>
    <p>или перетащите сюда</p>
    <UploadProgress v-if="uploading" :progress="progress" />
  </div>
</template>

<script>
import axios from 'axios'
import UploadProgress from './UploadProgress.vue'

export default {
  name: 'FileDropzone',
  components: { UploadProgress },
  data() {
    return {
      uploading: false,
      progress: 0
    }
  },
  methods: {
    openFileDialog() {
      this.$refs.fileInput.click()
    },
    async handleFileChange(event) {
      const file = event.target.files[0]
      if (!file || file.type !== 'video/mp4') {
        this.$toast.error('Пожалуйста, выберите видео в формате MP4.')
        return
      }

      this.uploading = true
      const formData = new FormData()
      formData.append('video', file)

      try {
        await axios.post('/api/upload', formData, {
          onUploadProgress: (e) => {
            this.progress = Math.round((e.loaded * 100) / e.total)
          }
        })
        this.$emit('file-selected', file)
      } catch (err) {
        this.$router.push({ name: 'Error' })
      } finally {
        this.uploading = false
      }
    },
    handleDrop(event) {
      const file = event.dataTransfer.files[0]
      if (file && file.type === 'video/mp4') {
        this.$refs.fileInput.files = event.dataTransfer.files
        this.handleFileChange(event)
      }
    }
  }
}
</script>

<style scoped>
.dropzone {
  border: 2px dashed #007bff;
  padding: 50px;
  text-align: center;
  cursor: pointer;
  margin: 20px auto;
  max-width: 500px;
}
</style>