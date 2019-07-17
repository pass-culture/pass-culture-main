export const getRedirectToOffersOrOfferers = ({ hasOffers, hasPhysicalVenues }) => {
  const hasOffersWithPhysicalVenues = hasOffers && hasPhysicalVenues
  return hasOffersWithPhysicalVenues || hasPhysicalVenues ? '/offres' : '/structures'
}

export const getRedirectToSignin = ({ pathname, search }) => {
  const fromUrl = encodeURIComponent(`${pathname}${search}`)
  return `/connexion?de=${fromUrl}`
}
