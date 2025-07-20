<template>
  <div id="app">
    <header>
      <img alt="Face Detector Logo" src="./assets/logo.png" />
      <h1>Face Detector</h1>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

header img {
  height: 40px;
  margin-right: 10px;
}
</style>