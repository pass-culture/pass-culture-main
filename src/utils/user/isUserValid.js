/**
 * @param  {Any}  user
 * @return {Object|Boolean} Retourne l'objet user si valide
 */
export const isValidUser = user =>
  (user && Boolean(user) && Boolean(user.publicName) && user) || false

export default isValidUser
