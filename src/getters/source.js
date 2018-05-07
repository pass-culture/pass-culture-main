import get from 'lodash.get'

export default function getSource(mediation, offer) {
  return (
    Object.assign({ sourceType: 'events' }, get(offer, 'eventOccurence.event')) ||
    Object.assign({ sourceType: 'things' }, get(offer, 'thing')) ||
    Object.assign({ sourceType: 'events' }, get(mediation, 'event')) ||
    Object.assign({ sourceType: 'things' }, get(mediation, 'thing'))
  )
}
