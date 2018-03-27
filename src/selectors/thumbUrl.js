import { createSelector } from 'reselect'
import get from 'lodash.get';
import { API_URL, THUMBS_URL } from '../utils/config'

import selectSource from './source'
import selectMediation from './mediation'
import selectOffer from './offer'

export default createSelector(
  (state, ownProps) => selectMediation(state, ownProps),
  (state, ownProps) => selectSource(state, ownProps),
  (state, ownProps) => selectOffer(state, ownProps),
  (mediation, source, offer) => {
    const sourceCollectionName =
      (get(offer, 'eventOccurence') && 'events') ||
      (get(offer, 'thing') && 'things') ||
      (get(mediation, 'event') && 'events') ||
      (get(mediation, 'thing') && 'things') || ''
    if (get(mediation, 'thumbCount') > 0) {
      return `${THUMBS_URL}/mediations/${mediation.id}`
    } else if (get(source, 'thumbCount') > 0) {
      return `${THUMBS_URL}/${sourceCollectionName}/${source.id}`
    } else {
      return`${API_URL}/static/images/default_thumb.png`
    }
  }
)
