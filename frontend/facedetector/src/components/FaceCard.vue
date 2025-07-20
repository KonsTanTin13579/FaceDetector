<template>
  <div class="face-card" @click="$emit('click')">
    <img :src="face.image" :alt="face.gender" width="100" />
    <p>{{ face.gender }}, {{ face.age }} лет</p>
  </div>
</template>

<script>
export default {
  name: 'FaceCard',
  props: {
    face: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.face-card {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.3s;
}
.face-card:hover {
  background-color: #f0f0f0;
}
</style>