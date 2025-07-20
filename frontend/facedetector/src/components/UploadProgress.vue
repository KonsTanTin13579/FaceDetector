<template>
  <div class="upload-progress">
    <div class="progress-bar" :style="{ width: progress + '%' }"></div>
    <p>Загрузка: {{ progress }}%</p>
  </div>
</template>

<script>
export default {
  name: 'UploadProgress',
  props: {
    progress: {
      type: Number,
      required: true
    }
  }
}
</script>

<style scoped>
.upload-progress {
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin: 10px 0;
}
.progress-bar {
  height: 20px;
  background-color: #007bff;
  text-align: center;
  line-height: 20px;
  color: white;
  transition: width 0.3s ease;
}
</style>