<template>
  <div class="not-found">
    <h1>{{ t('errors.notFound') }}</h1>
    <p>{{ t('errors.pageNotFound') }}</p>
    <div class="actions">
      <router-link to="/" class="home-btn">{{ t('nav.home') }}</router-link>
      <button @click="goBack" class="back-btn">{{ t('common.back') }}</button>
    </div>
    <div class="suggestions">
      <h3>{{ t('errors.suggestions') }}</h3>
      <ul>
        <li><router-link to="/">{{ t('nav.home') }}</router-link></li>
        <li><router-link to="/about">{{ t('nav.about') }}</router-link></li>
        <li><router-link to="/help">{{ t('nav.help') }}</router-link></li>
        <li><router-link to="/test">{{ t('nav.test') }}</router-link></li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.not-found {
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: var(--color-background);
}

.not-found-content {
  max-width: 600px;
  text-align: center;
  background: white;
  padding: 60px 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.error-code {
  font-size: 8rem;
  font-weight: bold;
  color: #3b82f6;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.not-found-content h1 {
  font-size: 2.5rem;
  color: #334155;
  margin-bottom: 15px;
}

.not-found-content p {
  font-size: 1.2rem;
  color: #64748b;
  margin-bottom: 40px;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 40px;
}

.home-btn,
.back-btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
}

.home-btn {
  background: #3b82f6;
  color: white;
}

.home-btn:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

.back-btn {
  background: #64748b;
  color: white;
}

.back-btn:hover {
  background: #475569;
  transform: translateY(-2px);
}

.suggestions {
  text-align: left;
  max-width: 400px;
  margin: 0 auto;
}

.suggestions h3 {
  color: #334155;
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.suggestions ul {
  list-style: none;
  padding: 0;
}

.suggestions li {
  margin-bottom: 10px;
}

.suggestions a {
  color: #3b82f6;
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.suggestions a:hover {
  color: #2563eb;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .not-found-content {
    padding: 40px 20px;
  }
  
  .error-code {
    font-size: 6rem;
  }
  
  .not-found-content h1 {
    font-size: 2rem;
  }
  
  .actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .home-btn,
  .back-btn {
    width: 100%;
  }
}
</style> 