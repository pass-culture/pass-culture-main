import createCachedSelector from 're-reselect'

import offersSelector from './offers'

export default createCachedSelector(
  (state, venueId, eventId) => offersSelector(state, venueId, eventId),
  offers => offers
    .reduce((aggreged, o) => {
      return o.offer && o.offer.reduce((subaggreged, offer) => {
        return {
          available: subaggreged.available + offer.available,
          groupSizeMin: subaggreged.groupSizeMin
            ? Math.min(subaggreged.groupSizeMin, offer.groupSize)
            : offer.groupSize,
          groupSizeMax: subaggreged.groupSizeMax
            ? Math.max(subaggreged.groupSizeMax, offer.groupSize)
            : offer.groupSize,
          priceMin: subaggreged.priceMin
            ? Math.min(subaggreged.priceMin, offer.price)
            : offer.price,
          priceMax: subaggreged.priceMax
            ? Math.max(subaggreged.priceMax, offer.price)
            : offer.price,
        }
      }, aggreged)
    }, {
      available: 0,
      groupSizeMin: 0,
      groupSizeMax: 0,
      priceMin: 0,
      priceMax: 0,
    })
)(
  (state, venueId, eventId) => `${venueId || ''}/${eventId || ''}`
)
