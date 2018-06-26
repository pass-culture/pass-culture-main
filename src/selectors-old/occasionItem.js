import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import { API_URL, THUMBS_URL } from '../utils/config'

export default (
  selectEvent,
  selectThing,
  selectMediations,
  selectOccurences
) => createSelector(
  selectEvent,
  selectThing,
  selectMediations,
  (state, ownProps) => get(ownProps, 'occasion.thumbPath'),
  selectOccurences,
  (event, thing, mediations, thumbPath, occurences) => {

    console.log('event', event, 'thing', thing)

    const occasionItem = {
      event,
      mediations,
      occurences,
      thing,
      thumbUrl: get(mediations, '0')
        ? `${THUMBS_URL}/mediations/${mediations[0].id}`
        : `${API_URL}${thumbPath}`
    }

    if (!occurences) {
      return occasionItem
    }

    occasionItem.maxDate = occurences.map(o =>
        moment(o.beginningDatetime)
      ).reduce((max, d) => max &&
        max.isAfter(d) ? max : d, null
      )

    Object.assign(occasionItem,
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

    return occasionItem
  }
)
