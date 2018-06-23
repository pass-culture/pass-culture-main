import { createSelector } from 'reselect'

export default (
  selectOccurences
) => createSelector(
  selectOccurences,
  occurences => occurences &&
    occurences.reduce((aggreged, o) => {
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
        groupSizeMin: null,
        groupSizeMax: null,
        priceMin: null,
        priceMax: null,
      })
)
