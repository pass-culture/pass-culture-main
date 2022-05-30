import {AUTH_LOGIN, AUTH_LOGOUT, AUTH_ERROR, AUTH_CHECK, AuthProvider} from 'react-admin';
import {UserManager} from 'oidc-client';

import getProfileFromToken from './getProfileFromToken'

const urlBase = process.env.REACT_APP_URL_BASE

const issuer = 'https://accounts.google.com/';
const OIDC_CLIENT_ID = process.env.REACT_APP_OIDC_CLIENT_ID
const OIDC_CLIENT_SECRET = process.env.REACT_APP_OIDC_CLIENT_SECRET
const OIDC_REDIRECT_URI = process.env.REACT_APP_OIDC_REDIRECT_URI

const userManager = new UserManager({
    authority: issuer,
    client_id: OIDC_CLIENT_ID,
    redirect_uri: OIDC_REDIRECT_URI,
    response_type: 'code',
    scope: 'openid email profile', // Allow to retrieve the email and user name later api side
});

const cleanup = () => {
    // Remove the ?code&state from the URL
    window.history.replaceState(
        {},
        window.document.title,
        window.location.origin
    );
}

const getInfoFromToken = async (token: string) => {
    const tokenObj = JSON.parse(token)
    const jwt = await fetch("https://oauth2.googleapis.com/tokeninfo?id_token=" + tokenObj.id_token, {
        method: "GET"
    })
    return {...jwt}
}

async function getTokenApiFromAuthToken() {
    let tokenApi;
    const token = localStorage.getItem('token')
    if (!token) {
        return null;
    }

    const authToken = JSON.parse(token)
    const response = await fetch(`http://localhost/backoffice/auth/token?token=${authToken.id_token}`)

    response.json().then(value => localStorage.setItem('tokenApi', value.token))
}

export const authProvider: AuthProvider = {
    // authentication
    async login(params) {
        const token = params.token

        localStorage.setItem('token', JSON.stringify(token));
        await getTokenApiFromAuthToken();
        await userManager.clearStaleState();
        cleanup();
        return Promise.resolve();
    },

    async checkError(error) {
        return Promise.resolve(error)
    },
    async checkAuth(params) {
        const token = localStorage.getItem('token');

        if (!token) {
            return Promise.reject()
        }

        // This is specific to the Google authentication implementation
        const jwt = getProfileFromToken(token);
        const now = new Date();

        // @ts-ignore
        return now.getTime() > (jwt.exp * 1000) ? Promise.reject() : Promise.resolve()
    },
    async logout() {
        localStorage.removeItem('token');
        return Promise.resolve();
    },
    async getIdentity() {
        const token = localStorage.getItem('token');
        const jwt = token ? getProfileFromToken(token) : '';

        return {
            id: 1,
            // @ts-ignore
            fullName: jwt.name,

            avatar:
            // @ts-ignore
            jwt.picture,
        }
    },
    // authorization
    async getPermissions(params) {
        return Promise.reject('Unknown method')
    },
}


export default authProvider;
