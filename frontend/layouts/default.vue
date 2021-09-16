<template>
  <div class="bg-gray-900 min-h-screen text-white">
    <div class="bg-gray-800 w-full flex flex-row p-4 h-18">
      <div class="w-16">
        <nuxt-link to="/">
          <img src="/img/logo.svg" />
        </nuxt-link>
      </div>
      <div class="flex-grow"></div>
      <section class="flex flex-col justify-center">
        <div class="text-white pr-4"><NuxtLink to="/choose_template">+</NuxtLink></div>
      </section>
      <section class="flex flex-col justify-center">
        <div class="text-white">
          <a
            href="https://auth.cloudserver.click/auth/realms/cloudserver-user/account/#/"
            >niwla23</a
          >
        </div>
      </section>
    </div>
    <main class="p-6 pt-8 lg:p-24 lg:pt-12 ">
      <Nuxt />
    </main>
  </div>
</template>


<style>
/* width */
::-webkit-scrollbar {
  width: 20px;
}

/* Track */
::-webkit-scrollbar-track {
  box-shadow: inset 0 0 5px grey;
  border-radius: 10px;
}

/* Handle */
::-webkit-scrollbar-thumb {
  background: red;
  border-radius: 10px;
}

/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
  background: #b30000;
}

* {
  scrollbar-width: thin; /* "auto" or "thin" */
  scrollbar-color: #1f2937 #111827; /* scroll thumb and track */
}
</style>
