import get from 'lodash.get'
import createCachedSelector from 're-reselect'

const mapArgsToCacheKey = (state, event, thing, offerer, venue) =>
  `${get(event, 'id', ' ')}/${get(thing, 'id', ' ')}/
   ${get(offerer, 'id', ' ')}/${get(venue, 'id', ' ')}`

export const selectEventOrThingPatchByEventAndThingAndOfferAndOffererAndVenue = createCachedSelector(
  (state, event) => event,
  (state, event, thing) => thing,
  (state, event, thing, offer) => offer,
  (state, event, thing, offer, offerer) => offerer,
  (state, event, thing, offer, offerer, venue) => venue,
  (event, thing, offer, offerer, venue) =>
    Object.assign(
      {
        bookingEmail: get(offer, 'bookingEmail'),
        offererId: get(offerer, 'id'),
        venueId: get(venue, 'id'),
        type: event
          ? get(event, 'offerType.value', '')
          : thing && thing.offerType.value,
      },
      event || thing
    )
)(mapArgsToCacheKey)

export default selectEventOrThingPatchByEventAndThingAndOfferAndOffererAndVenue
