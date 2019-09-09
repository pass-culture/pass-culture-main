const userHasNoOffersInAPhysicalVenueYet = currentUser => {
  const offererHasNoOffer = !currentUser.hasOffers
  const offererHasOnlyDigitalOffers = currentUser.hasOffers && !currentUser.hasPhysicalVenues

  return offererHasNoOffer || offererHasOnlyDigitalOffers
}

export default userHasNoOffersInAPhysicalVenueYet
