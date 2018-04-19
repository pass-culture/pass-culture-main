import get from 'lodash.get'

import { THUMBS_URL } from '../utils/config'

export default function getThumbUrl (mediation, source, offer) {
  const sourceCollectionName =
    (get(offer, 'eventOccurence') && 'events') ||
    (get(offer, 'thing') && 'things') ||
    (get(mediation, 'event') && 'events') ||
    (get(mediation, 'thing') && 'things') || ''
  if (get(mediation, 'thumbCount') > 0) {
    return `${THUMBS_URL}/mediations/${mediation.id}`
  } else if (get(source, 'thumbCount') > 0) {
    return `${THUMBS_URL}/${sourceCollectionName}/${source.id}`
  }
}
