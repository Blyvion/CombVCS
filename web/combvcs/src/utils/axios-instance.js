import axios from 'axios';
const axiosApi = axios.create({
    baseURL: 'http://127.0.0.1:32001',
    timeout: 120000,
    withCredentials: true,
    headers: {
        'Content-Type': 'multipart/form-data',
    },
});
export default axiosApi;
