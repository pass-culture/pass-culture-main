import currentUserUUID from './currentUserUUID'

export default userFromRequest => {
  if (!userFromRequest) {
    return null
  }
  return Object.assign({ currentUserUUID }, userFromRequest)
}
