<template>
  <div class="error-page">
    <h1>Ошибка</h1>
    <p>Видео не может быть обработано. Попробуйте загрузить другое видео.</p>
    <button @click="goToUpload">Вернуться на главную</button>
  </div>
</template>

<script>
export default {
  name: 'ErrorPage',
  methods: {
    goToUpload() {
      this.$router.push({ name: 'Upload' })
    }
  }
}
</script>

<style scoped>
.error-page {
  text-align: center;
}
button {
  padding: 10px 20px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>