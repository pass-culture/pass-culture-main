import { AuthProvider } from 'react-admin'
import { UserManager } from 'oidc-client'

import { getProfileFromToken } from './getProfileFromToken'
import { env } from '../libs/environment/env'

const userManager = new UserManager({
  authority: env.AUTH_ISSUER,
  client_id: env.OIDC_CLIENT_ID,
  redirect_uri: env.REDIRECT_URI,
  response_type: 'code',
  scope: 'openid email profile', // Allow to retrieve the email and user name later api side
})

const cleanup = () => {
  // Remove the ?code&state from the URL
  window.history.replaceState({}, window.document.title, window.location.origin)
}

async function getTokenApiFromAuthToken() {
  const token = localStorage.getItem('token')
  if (!token) {
    return null
  }

  const authToken = JSON.parse(token)
  try {
    const response = await fetch(
      `${env.API_URL}/auth/token?token=${authToken.id_token}`
    )
    if (!response.ok) {
      throw new Error(response.statusText)
    }
    const res = await response.json()
    localStorage.setItem('tokenApi', res.token)
  } catch (error) {
    alert("Une erreur s'est produite. On répare ça au plus vite !")
  }
}

export const authProvider: AuthProvider = {
  // authentication
  async login(params) {
    const token = params.token

    try {
      localStorage.setItem('token', JSON.stringify(token))
      await getTokenApiFromAuthToken()

      const tokenApi = localStorage.getItem('tokenApi')
      if (!tokenApi) {
        return Promise.reject('No Token Found')
      }

      await userManager.clearStaleState()
      cleanup()
      return Promise.resolve()
    } catch (error) {
      throw error
    }
  },
  async checkError(error) {
    return Promise.reject(error)
  },
  async checkAuth(params) {
    const token = localStorage.getItem('token')

    if (!token) {
      return Promise.reject('No Token Found')
    }

    // This is specific to the Google authentication implementation
    const jwt = getProfileFromToken(token)
    const now = new Date()

    // @ts-ignore
    return now.getTime() > jwt.exp * 1000 ? Promise.reject() : Promise.resolve()
  },
  async logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('tokenApi')
    return Promise.resolve()
  },
  async getIdentity() {
    const token = localStorage.getItem('token')
    const jwt: any = token ? getProfileFromToken(token) : ''

    return {
      id: jwt.sub,
      fullName: jwt.name,
      avatar: jwt.picture,
    }
  },
  // authorization
  getPermissions(params) {
    return Promise.reject('Unknown method')
  },
}
