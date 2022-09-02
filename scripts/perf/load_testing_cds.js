import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { describe, expect } from 'https://jslib.k6.io/k6chaijs/4.3.4.0/index.js';
import { SharedArray } from 'k6/data';
import { scenario } from 'k6/execution';

// const data = new SharedArray('users', function () {
//   return JSON.parse(open('./data.json')).users;
// });

const payload = JSON.stringify({
    identifier: "",
    password: ""
});

const params = {
    headers: {
        'Content-Type': 'application/json',
    },
};

var booking_id;

/*
VU virtual users :
k6 works with the concept of virtual users (VUs), which run your test scripts.
VUs are essentially parallel while(true) loops.
*/

export const options = {
    stages: [
        // { target: 25, duration: '5m' },
        // { target: 20, duration: '5m' },
        // { target: 15, duration: '5m' },
        { target: 1, duration: '1s' },
    ],
    // scenarios: {
    //   login: {
    //     executor: 'per-vu-iterations',
    //     vus: users.length,
    //     iterations: 1,
    //     maxDuration: '30m',
    //   },
    // },
};


export default function testSuite() {

    // STEP 1 - USER LOGIN
    group('User login at https://backend.testing.passculture.team/native/v1/signin', () => {

        const LOGIN_URL = 'https://backend.testing.passculture.team/native/v1/signin'



        const response = http.post(LOGIN_URL, payload, params, {
            tags: {
                my_tag: "user login step",
            },
        });

        check(response, { 'login - status was 200': (r) => r.status === 200 });
        const data = response.json()
        const token = data.accessToken
        params['headers']["Authorization"] = 'Bearer ' + token

    });

    // STEP 2 - GET CDS OFFER 
    group('get_offer cds https://backend.testing.passculture.team/native/v1/offer/3420', () => {

        const OFFER_URL = 'https://backend.testing.passculture.team/native/v1/offer/3420'
        const offer = http.get(OFFER_URL, params, {
            tags: {
                my_tag: "user consult cds offer - trigger cds call",
            },
        });
        //console.log(offer)
        check(offer, { 'get_offer - status was 200': (r) => r.status === 200 });
    });


    //STEP 3 - BOOK OFFER CDS
    group('booking offer cds https://backend.testing.passculture.team/native/v1/bookings', () => {
        console.log(params)
        const BOOKING_URL = 'https://backend.testing.passculture.team/native/v1/bookings'
        const payload = JSON.stringify({ quantity: 1, stockId: 3348 })

        const booking = http.post(BOOKING_URL, payload, params, {
            tags: {
                my_tag: "user book cds offer",
            },
        });
        console.log(booking)
        check(booking, { 'book_offer - status was 200': (r) => r.status === 200 });
        const data = booking.json()
        booking_id = data.bookingId
        console.log(booking_id)


    });

    //wait a little bit 
    sleep(5);

    // CANCEL OFFER
    group('cancel booking cds https://backend.testing.passculture.team/native/v1/bookings/id/cancel', () => {
        console.log(booking_id)
        const CANCEL_URL = 'https://backend.testing.passculture.team/native/v1/bookings/' + booking_id + '/cancel'
        const payload = JSON.stringify({})

        const cancel_booking = http.post(CANCEL_URL, payload, params, {
            tags: {
                my_tag: "cancel book cds",
            },
        });
        console.log(cancel_booking)
        check(cancel_booking, { 'cancel booking - status was 204': (r) => r.status === 204 });



    });



}