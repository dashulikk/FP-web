import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    scenarios: {
        // (Constant VUs)
        constant_load: {
            executor: 'constant-vus',
            vus: 10, // Кількість постійних користувачів
            duration: '1m', // Тривалість тесту
        },

        // (Ramping VUs)
        ramping_load: {
            executor: 'ramping-vus',
            startVUs: 1,
            stages: [
                { duration: '30s', target: 10 }, // За 30 секунд збільшення до 10 користувачів
                { duration: '30s', target: 20 }, // За наступні 30 секунд збільшення до 20 користувачів
                { duration: '1m', target: 0 }, // Зменшення до 0
            ],
            gracefulRampDown: '10s',
        },

        // (Constant Arrival Rate)
        constant_rate: {
            executor: 'constant-arrival-rate',
            rate: 20, // 20 запитів на секунду
            timeUnit: '1s', // Частота - кожна секунда
            duration: '1m', // Тривалість тесту
            preAllocatedVUs: 10, // Початкова кількість користувачів
            maxVUs: 100, // Максимальна кількість користувачів
        }
    }
};

export default function () {

    let productId = 1;
    let res1 = http.get(`http://127.0.0.1:8000/products/${productId}`);
    check(res1, { 'status is 200': (r) => r.status === 200 });
    sleep(1);
    let res2 = http.get('http://127.0.0.1:8000/external-api');
    check(res2, { 'status is 200': (r) => r.status === 200 });

    let res3 = http.get('http://127.0.0.1:8000/users');
    check(res3, { 'status is 200': (r) => r.status === 200 });

    sleep(1);
}
