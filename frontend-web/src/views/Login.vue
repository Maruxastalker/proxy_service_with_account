<template>
  <v-container class="fill-height">
    <v-row justify="center">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-center text-h4 py-4">
            Вход
          </v-card-title>
          
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                :rules="[rules.required]"
                outlined
              />
              
              <v-text-field
                v-model="password"
                label="Пароль"
                type="password"
                :rules="[rules.required]"
                outlined
              />
              
              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                :loading="loading"
              >
                Войти
              </v-btn>
            </v-form>
          </v-card-text>
          
          <v-card-actions class="justify-center">
            <router-link to="/register">Нет аккаунта? Зарегистрироваться</router-link>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)

const rules = {
  required: (v) => !!v || 'Обязательное поле',
}

async function handleLogin() {
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push('/profile')
  } catch (error) {
    alert(error.response?.data?.detail || 'Ошибка входа')
  } finally {
    loading.value = false
  }
}
</script>