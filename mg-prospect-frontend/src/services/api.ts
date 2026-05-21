import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const api = axios.create({
    baseURL: API_BASE_URL,
});

// Injeta o token em todas as requisições
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('mg_token');
    if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Intercepta respostas com erro 401 e desloga o usuário
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('mg_token');
            window.location.href = '/';
        }
        return Promise.reject(error);
    }
);