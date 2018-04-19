import get from 'lodash.get';

export default function getVenue (source, offer) {
  return get(offer, 'eventOccurence.venue') ||
    get(offer, 'venue') ||
    get(source, 'eventOccurence.venue') ||
    get(source, 'venue')
}
