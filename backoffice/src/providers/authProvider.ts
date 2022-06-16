import { UserManager } from 'oidc-client'
import { AuthProvider } from 'react-admin'

import { env } from '../libs/environment/env'
import { eventMonitoring } from '../libs/monitoring/sentry'

import { getProfileFromToken } from './getProfileFromToken'
import { AuthToken } from './types'

const userManager = new UserManager({
  authority: env.AUTH_ISSUER,
  client_id: env.OIDC_CLIENT_ID,
  redirect_uri: env.OIDC_REDIRECT_URI,
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
      eventMonitoring.captureException(response.statusText)
    }
    const res = await response.json()
    localStorage.setItem('tokenApi', res.token)
  } catch (error) {
    eventMonitoring.captureException(error)
    throw error
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
        throw new Error('NO_TOKEN_API')
      }

      await userManager.clearStaleState()
      cleanup()
    } catch (error) {
      eventMonitoring.captureException(error)
      throw error
    }
  },
  checkError(error) {
    console.log('checkError', error)
    // if (status === 401 || status === 403) {
    //   localStorage.removeItem('username');
    //   return Promise.reject();
    // }
    eventMonitoring.captureException(error)
    throw error
  },
  async checkAuth() {
    const token = localStorage.getItem('token')

    if (!token) {
      throw new Error('No Token Found')
    }

    // This is specific to the Google authentication implementation
    const jwt = getProfileFromToken(token)
    const now = new Date()

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore 12356
    if (now.getTime() > jwt.exp * 1000) {
      throw new Error('EXPIRED_TOKEN')
    }
  },
  async logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('tokenApi')
  },
  async getIdentity() {
    try {
      const token = localStorage.getItem('token')
      const jwt: AuthToken = getProfileFromToken(token as string)

      return {
        id: jwt.sub,
        fullName: jwt.name,
        avatar: jwt.picture,
      }
    } catch (error) {
      throw new Error('Pas de token en mémoire')
    }
  },
  // authorization
  getPermissions() {
    throw new Error('Unknown method')
  },
}
