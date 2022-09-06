import jwtDecode from 'jwt-decode'

import { AuthToken } from './types'

export const getProfileFromToken = (tokenJson: string) => {
  const token = JSON.parse(tokenJson)
  return jwtDecode<AuthToken>(token)
}
