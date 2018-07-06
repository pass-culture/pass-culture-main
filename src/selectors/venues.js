import createCachedSelector from 're-reselect';

export default createCachedSelector(
  state => state.data.venues,
  (state, optionalOffererId) => optionalOffererId,
  (venues, optionalOffererId) => {
    if (optionalOffererId)
      return venues.filter(v => v.managingOffererId === optionalOffererId)
    return venues
  },
  (state, optionalOffererId) => optionalOffererId
)
