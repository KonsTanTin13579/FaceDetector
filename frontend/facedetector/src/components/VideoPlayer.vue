<template>
  <video :src="videoUrl" controls width="640" height="360"></video>
</template>

<script>
export default {
  name: 'VideoPlayer',
  props: {
    videoUrl: {
      type: String,
      required: true
    }
  }
}
</script>