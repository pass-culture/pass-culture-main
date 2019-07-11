export const isValidUser = user =>
  (user && Boolean(user) && Boolean(user.publicName) && user) || false

export default isValidUser
