import get from 'lodash.get'

export default function getSource(mediation, offer) {
  return (
    get(offer, 'eventOccurence.event') ||
    get(offer, 'thing') ||
    get(mediation, 'event') ||
    get(mediation, 'thing')
  )
}
