import currentUserUUID from '../../../../selectors/data/currentUserSelector/currentUserUUID'

export default userFromRequest => {
  if (!userFromRequest) {
    return null
  }
  return Object.assign({ currentUserUUID }, userFromRequest)
}
