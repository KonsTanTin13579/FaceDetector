<template>
  <div class="face-details-page">
    <h2>Детали лица</h2>
    <img :src="selectedFace.image" alt="Face" width="150" />
    <p>Пол: {{ selectedFace.gender }}</p>
    <p>Возраст: {{ selectedFace.age }} лет</p>
    <p>Время появления:</p>
    <ul>
      <li v-for="(time, index) in selectedFace.times" :key="index">
        {{ time }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'FaceDetailsPage',
  data() {
    return {
      faces: [
        {
          id: 1,
          gender: 'Женщина',
          age: 25,
          image: 'https://via.placeholder.com/100 ',
          times: ['0:12 - 0:25', '0:45 - 1:10']
        },
        {
          id: 2,
          gender: 'Мужчина',
          age: 32,
          image: 'https://via.placeholder.com/100 ',
          times: ['0:30 - 0:40']
        }
      ],
      selectedFace: {}
    }
  },
  mounted() {
    const faceId = this.$route.params.faceId
    this.selectedFace = this.faces.find(face => face.id === Number(faceId))
  }
}
</script>