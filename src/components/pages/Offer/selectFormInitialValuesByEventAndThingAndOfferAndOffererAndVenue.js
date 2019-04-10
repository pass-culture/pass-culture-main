import get from 'lodash.get'
import createCachedSelector from 're-reselect'

const mapArgsToCacheKey = (state, event, thing, offerer, venue) =>
  `${get(event, 'id', ' ')}/${get(thing, 'id', ' ')}/
   ${get(offerer, 'id', ' ')}/${get(venue, 'id', ' ')}`

export const selectFormInitialValuesByEventAndThingAndOfferAndOffererAndVenue = createCachedSelector(
  (state, event) => event,
  (state, event, thing) => thing,
  (state, event, thing, offer) => offer,
  (state, event, thing, offer, offerer) => offerer,
  (state, event, thing, offer, offerer, venue) => venue,
  (event, thing, offer, offerer, venue) => {
    const {
      bookingEmail,
      description,
      condition,
      ageMin,
      ageMax,
      durationMinutes,
      extraData,
      isNational,
      mediaUrls,
      name,
      type,
      url,
    } = offer || {}
    const eventOrThing = event || thing || {}

    const formInitialValues = {
      ageMin: ageMin || eventOrThing.ageMin,
      ageMax: ageMax || eventOrThing.ageMax,
      condition: condition || eventOrThing.condition,
      description: description || eventOrThing.description,
      durationMinutes: durationMinutes || eventOrThing.durationMinutes,
      extraData: Object.assign({}, eventOrThing.extraData, extraData),
      isNational: isNational || eventOrThing.isNational,
      mediaUrls: mediaUrls || eventOrThing.mediaUrls,
      name: name || eventOrThing.name,
      type: type || get(eventOrThing, 'offerType.value', ''),
      url: url || eventOrThing.url,
    }
    return Object.assign(formInitialValues, {
      bookingEmail,
      offererId: get(offerer, 'id'),
      venueId: get(venue, 'id'),
    })
  }
)(mapArgsToCacheKey)

export default selectFormInitialValuesByEventAndThingAndOfferAndOffererAndVenue
