<template>
  <div class="face-details">
    <div class="face-image">
      <img :src="face.image" :alt="`Лицо ${face.id}`" />
    </div>
    <div class="face-info">
      <h3>Информация о лице</h3>
      <p><strong>Пол:</strong> {{ face.gender || 'Не определён' }}</p>
      <p><strong>Возраст:</strong> {{ face.age || 'Не определён' }}</p>
      <p><strong>Эмоция:</strong> {{ face.emotion || 'Не определена' }}</p>
      <p><strong>Цвет кожи:</strong> {{ face.skinTone || 'Не определён' }}</p>

      <div v-if="face.times && face.times.length">
        <h4>Время появления в видео:</h4>
        <ul>
          <li v-for="(time, index) in face.times" :key="index">
            {{ time }}
          </li>
        </ul>
      </div>

      <button @click="downloadFace">Скачать информацию</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FaceDetails',
  props: {
    face: {
      type: Object,
      required: true,
      default: () => ({
        id: 0,
        gender: '',
        age: '',
        emotion: '',
        skinTone: '',
        image: 'https://via.placeholder.com/150 ',
        times: []
      })
    }
  },
  methods: {
    downloadFace() {
      const dataStr = JSON.stringify(this.face, null, 2);
      const blob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.download = `face-${this.face.id}.json`;
      link.click();

      URL.revokeObjectURL(url);
    }
  }
}
</script>

<style scoped>
.face-details {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 30px;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.face-image img {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.face-info {
  text-align: left;
}

.face-info h3 {
  margin-top: 0;
}

.face-info p {
  margin: 5px 0;
}

.face-info ul {
  list-style: none;
  padding-left: 0;
}

.face-info li {
  padding: 2px 0;
}

button {
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #0056b3;
}
</style>