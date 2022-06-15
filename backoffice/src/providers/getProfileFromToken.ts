import jwtDecode from 'jwt-decode'

export const getProfileFromToken = (tokenJson: string) => {
  const token = JSON.parse(tokenJson)

  const jwt = jwtDecode(token.id_token)
  return jwt
}
