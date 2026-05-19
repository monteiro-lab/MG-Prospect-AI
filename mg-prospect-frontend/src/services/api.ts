import axios from 'axios';

export const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
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