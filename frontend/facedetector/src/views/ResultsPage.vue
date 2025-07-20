<template>
  <div class="results-page">
    <h2>Всего лиц в видео: {{ faces.length }}</h2>
    <div class="face-cards">
      <FaceCard
          v-for="(face, index) in faces"
          :key="index"
          :face="face"
          @click="showFaceDetails(face)"
      />
    </div>
  </div>
</template>

<script>
import FaceCard from '../components/FaceCard.vue'

export default {
  name: 'ResultsPage',
  components: { FaceCard },
  data() {
    return {
      faces: [
        { id: 1, gender: 'Женщина', age: 25, image: 'https://via.placeholder.com/100 ' },
        { id: 2, gender: 'Мужчина', age: 32, image: 'https://via.placeholder.com/100 ' }
      ]
    }
  },
  methods: {
    showFaceDetails(face) {
      this.$router.push({ name: 'FaceDetails', params: { faceId: face.id } })
    }
  }
}
</script>

<style scoped>
.face-cards {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 15px;
}
</style>