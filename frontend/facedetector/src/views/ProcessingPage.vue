<template>
  <div class="processing-page">
    <h1>Обработка видео...</h1>
    <p>Файл: {{ file.name }} ({{ fileSize }} МБ)</p>
  </div>
</template>

<script>
export default {
  name: 'ProcessingPage',
  props: {
    file: {
      type: File,
      required: true
    }
  },
  computed: {
    fileSize() {
      return (this.file.size / 1024 / 1024).toFixed(2)
    }
  }
}
</script>