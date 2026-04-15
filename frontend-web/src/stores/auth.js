import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token'),
  }),
  
  actions: {
    async register(email, password, passwordConfirm) {
      const response = await api.post('/auth/register', {
        email,
        password,
        password_confirm: passwordConfirm,
      })
      this.token = response.data.access_token
      localStorage.setItem('access_token', this.token)
      await this.fetchUser()
      return response.data
    },
    
    async login(email, password) {
      const response = await api.post('/auth/login', { email, password })
      this.token = response.data.access_token
      localStorage.setItem('access_token', this.token)
      await this.fetchUser()
      return response.data
    },
    
    async fetchUser() {
      const response = await api.get('/users/me')
      this.user = response.data
    },
    
    async changePassword(oldPassword, newPassword) {
      await api.post('/users/change-password', {
        old_password: oldPassword,
        new_password: newPassword,
      })
    },
    
    async renewKey() {
      const response = await api.post('/users/renew-key')
      return response.data
    },
    
    async getMyKey() {
      const response = await api.get('/users/my-key')
      return response.data
    },
    
    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('access_token')
    },
  },
})