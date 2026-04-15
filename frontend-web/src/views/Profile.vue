<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4">Личный кабинет</v-card-title>
          
          <v-card-text>
            <v-list>
              <v-list-item>
                <v-list-item-title>Email</v-list-item-title>
                <v-list-item-subtitle>{{ authStore.user?.email }}</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>Ключ активации</v-list-item-title>
                <v-list-item-subtitle>
                  <v-chip :color="activationKey ? 'success' : 'warning'">
                    {{ activationKey ? 'Активен' : 'Не создан' }}
                  </v-chip>
                </v-list-item-subtitle>
                <v-list-item-subtitle v-if="activationKey">
                  Ключ: {{ activationKey }}
                </v-list-item-subtitle>
                <v-list-item-subtitle v-if="expiresAt">
                  Истекает: {{ new Date(expiresAt).toLocaleString() }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
          
          <v-card-actions>
            <v-btn color="primary" @click="handleRenewKey" :loading="renewLoading">
              Обновить ключ
            </v-btn>
            <v-btn color="info" @click="showChangePassword = true">
              Сменить пароль
            </v-btn>
            <v-btn color="error" @click="handleLogout">
              Выйти
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    
    <v-dialog v-model="showChangePassword" max-width="500">
      <v-card>
        <v-card-title>Смена пароля</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="handleChangePassword">
            <v-text-field
              v-model="oldPassword"
              label="Старый пароль"
              type="password"
              required
            />
            <v-text-field
              v-model="newPassword"
              label="Новый пароль"
              type="password"
              :rules="[v => v.length >= 6 || 'Минимум 6 символов']"
              required
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="showChangePassword = false">Отмена</v-btn>
          <v-btn color="primary" @click="handleChangePassword" :loading="passwordLoading">
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activationKey = ref('')
const expiresAt = ref(null)
const renewLoading = ref(false)
const passwordLoading = ref(false)
const showChangePassword = ref(false)
const oldPassword = ref('')
const newPassword = ref('')

async function loadKey() {
  try {
    const data = await authStore.getMyKey()
    activationKey.value = data.activation_key
    expiresAt.value = data.expires_at
  } catch (error) {
    console.error('Ошибка загрузки ключа', error)
  }
}

async function handleRenewKey() {
  renewLoading.value = true
  try {
    const data = await authStore.renewKey()
    activationKey.value = data.activation_key
    expiresAt.value = data.expires_at
    alert('Новый ключ отправлен на почту')
  } catch (error) {
    alert('Ошибка обновления ключа')
  } finally {
    renewLoading.value = false
  }
}

async function handleChangePassword() {
  passwordLoading.value = true
  try {
    await authStore.changePassword(oldPassword.value, newPassword.value)
    alert('Пароль успешно изменен')
    showChangePassword.value = false
    oldPassword.value = ''
    newPassword.value = ''
  } catch (error) {
    alert('Ошибка смены пароля')
  } finally {
    passwordLoading.value = false
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchUser()
  }
  await loadKey()
})
</script>