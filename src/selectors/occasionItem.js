import moment from 'moment'
import { createSelector } from 'reselect'

export default selectOccurences => createSelector(
  selectOccurences,
  occurences => {
    if (!occurences) {
      return
    }

    const maxDate = occurences.map(o =>
        moment(o.beginningDatetime)
      ).reduce((max, d) => max &&
        max.isAfter(d) ? max : d, null
      )

    const {
      available,
      groupSizeMin,
      groupSizeMax,
      priceMin,
      priceMax,
    } = occurences.reduce((aggreged, o) => {
      return o.offer.reduce((subaggreged, offer) => {
        return {
          available: subaggreged.available + offer.available,
          groupSizeMin: subaggreged.groupSizeMin ? Math.min(subaggreged.groupSizeMin, offer.groupSize) : offer.groupSize,
          groupSizeMax: subaggreged.groupSizeMax ? Math.max(subaggreged.groupSizeMax, offer.groupSize) : offer.groupSize,
          priceMin: subaggreged.priceMin ? Math.min(subaggreged.priceMin, offer.price) : offer.price,
          priceMax: subaggreged.priceMax ? Math.max(subaggreged.priceMax, offer.price) : offer.price,
        }
      }, aggreged)
    }, {
      available: 0,
      groupSizeMin: null,
      groupSizeMax: null,
      priceMin: null,
      priceMax: null,
    })

    return {
      available,
      groupSizeMin,
      groupSizeMax,
      maxDate,
      priceMin,
      priceMax
    }
  }
)
