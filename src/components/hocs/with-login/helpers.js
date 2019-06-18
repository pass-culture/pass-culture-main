export const getRedirectToSignin = ({ pathname, search }) => {
  const fromUrl = encodeURIComponent(`${pathname}${search}`)
  return `/connexion?de=${fromUrl}`
}
