import { googleLogout } from '@react-oauth/google'
import decodeJwt from 'jwt-decode'
import { UserManager } from 'oidc-client'
import { AuthProvider } from 'react-admin'

import { env } from '../libs/environment/env'
import { eventMonitoring } from '../libs/monitoring/sentry'

import { getErrorMessage } from './apiHelpers'
import { getProfileFromToken } from './getProfileFromToken'
import { AuthToken, tokenApiPayload } from './types'

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
    const response = await fetch(`${env.API_URL}/auth/token?token=${authToken}`)
    if (!response.ok) {
      eventMonitoring.captureException(response.statusText)
    }
    const res = await response.json()
    localStorage.setItem('tokenApi', JSON.stringify(res.token))
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
        throw new Error(getErrorMessage('errors.token.api'))
      }

      await userManager.clearStaleState()
      const decodedToken: tokenApiPayload = decodeJwt(tokenApi)
      const permissions = JSON.stringify(decodedToken.perms)
      localStorage.setItem('permissions', permissions)
      cleanup()
    } catch (error) {
      eventMonitoring.captureException(error)
      throw error
    }
  },
  checkError(error) {
    // if (status === 401 || status === 403) {
    //   localStorage.removeItem('username');
    // }
    eventMonitoring.captureException(error)
    throw error
  },
  async checkAuth() {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error(getErrorMessage('errors.token.login'))
    }

    // This is specific to the Google authentication implementation
    const jwt = getProfileFromToken(token)
    const now = new Date()

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore 12356
    if (now.getTime() > jwt.exp * 1000) {
      throw new Error(getErrorMessage('errors.token.expired'))
    }
  },
  async logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('tokenApi')
    localStorage.removeItem('permissions')
    googleLogout()
  },
  async getIdentity() {
    try {
      const token = localStorage.getItem('token')
      const jwt: AuthToken = getProfileFromToken(
        JSON.stringify(token) as string
      )

      return {
        id: jwt.sub,
        fullName: jwt.name,
        avatar: jwt.picture,
      }
    } catch (error) {
      throw new Error(getErrorMessage('errors.token.notFound'))
    }
  },
  // authorization
  getPermissions() {
    const permissionString = localStorage.getItem('permissions')
    try {
      return permissionString
        ? Promise.resolve(JSON.parse(permissionString))
        : Promise.reject()
    } catch (error) {
      throw new Error(getErrorMessage('errors.permissions.notFound'))
    }
  },
}
