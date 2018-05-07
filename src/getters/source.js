import get from 'lodash.get'

import { THUMBS_URL } from '../utils/config'

export default function (offer) {
  const source = {}
  let event, mediation, thing
  event = get(offer, 'eventOccurence.event')
  if (event) {
    Object.assign(source, { sourceType: 'events' }, event)
  } else {
    thing = get(offer, 'thing')
    if (thing) {
      Object.assign(source, { sourceType: 'things' }, thing)
    } else {
      mediation = get(mediation, 'event')
      if (mediation) {
        Object.assign(source, { sourceType: 'events' }, mediation)
      } else {
        mediation = get(mediation, 'thing')
        Object.assign(source, { sourceType: 'things' }, thing)
      }
    }
  }
  if (source.thumbCount) {
    source.thumbUrl = `${THUMBS_URL}/${source.sourceType}/${source.id}`
  }
  if (source.mediations && source.mediations.length) {
    source.thumbUrl = `${THUMBS_URL}/mediations/${source.mediations[0].id}`
  }
  return source
}
