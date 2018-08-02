import createCachedSelector from 're-reselect'

import offersSelector from './offers'

export default createCachedSelector(
  (state, venueId, eventId) => offersSelector(state, venueId, eventId),
  offers =>
    offers.reduce(
      (aggreged, offer) => ({
        available: aggreged.available + offer.available,
        groupSizeMin: aggreged.groupSizeMin
          ? Math.min(aggreged.groupSizeMin, offer.groupSize)
          : offer.groupSize,
        groupSizeMax: aggreged.groupSizeMax
          ? Math.max(aggreged.groupSizeMax, offer.groupSize)
          : offer.groupSize,
        priceMin: aggreged.priceMin
          ? Math.min(aggreged.priceMin, offer.price)
          : offer.price,
        priceMax: aggreged.priceMax
          ? Math.max(aggreged.priceMax, offer.price)
          : offer.price,
      }),
      {
        available: 0,
        groupSizeMin: 0,
        groupSizeMax: 0,
        priceMin: 0,
        priceMax: 0,
      }
    )
)((state, venueId, eventId) => `${venueId || ''}/${eventId || ''}`)
