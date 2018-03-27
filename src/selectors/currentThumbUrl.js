import { createSelector } from 'reselect'
import get from 'lodash.get';
import { API_URL, THUMBS_URL } from '../utils/config'

import selectCurrentSource from './currentSource'
import selectCurrentMediation from './currentMediation'
import selectCurrentOffer from './currentOffer'

export default createSelector(
  state => selectCurrentMediation(state),
  state => selectCurrentSource(state),
  state => selectCurrentOffer(state),
  (currentMediation, currentSource, currentOffer) => {
    const sourceCollectionName =
      (get(currentOffer, 'eventOccurence') && 'eventOccurences') ||
      (get(currentOffer, 'thing') && 'things') ||
      (get(currentMediation, 'event') && 'events') ||
      (get(currentMediation, 'thing') && 'things') || ''

    if (get(currentMediation, 'thumbCount') > 0) {
      return `${THUMBS_URL}/mediations/${currentMediation.id}`
    } else if (get(currentSource, 'thumbCount') > 0) {
      return `${THUMBS_URL}/${sourceCollectionName}/${currentSource.id}`
    } else {
      return`${API_URL}/static/images/default_thumb.png`
    }
  }
)
