<template>
  <v-container class="fill-height">
    <v-row justify="center">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-center text-h4 py-4">
            Регистрация
          </v-card-title>
          
          <v-card-text>
            <v-form @submit.prevent="handleRegister">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                :rules="[rules.required, rules.email]"
                outlined
              />
              
              <v-text-field
                v-model="password"
                label="Пароль"
                type="password"
                :rules="[rules.required, rules.minLength]"
                outlined
              />
              
              <v-text-field
                v-model="passwordConfirm"
                label="Подтверждение пароля"
                type="password"
                :rules="[rules.required, rules.passwordMatch]"
                outlined
              />
              
              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                :loading="loading"
              >
                Зарегистрироваться
              </v-btn>
            </v-form>
          </v-card-text>
          
          <v-card-actions class="justify-center">
            <router-link to="/login">Уже есть аккаунт? Войти</router-link>
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
const passwordConfirm = ref('')
const loading = ref(false)

const rules = {
  required: (v) => !!v || 'Обязательное поле',
  email: (v) => /.+@.+\..+/.test(v) || 'Введите корректный email',
  minLength: (v) => v.length >= 6 || 'Пароль должен быть минимум 6 символов',
  passwordMatch: (v) => v === password.value || 'Пароли не совпадают',
}

async function handleRegister() {
  loading.value = true
  try {
    await authStore.register(email.value, password.value, passwordConfirm.value)
    router.push('/profile')
  } catch (error) {
    alert(error.response?.data?.detail || 'Ошибка регистрации')
  } finally {
    loading.value = false
  }
}
</script>