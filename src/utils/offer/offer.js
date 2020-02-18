export const checkOfferCannotBeBooked = (offer) => {
  return offer.isNotBookable || offer.isFullyBooked
}
