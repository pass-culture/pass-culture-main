import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import { getValueFromOfferOrProduct } from './getValueFromOfferOrProduct'

const mapArgsToCacheKey = (state, event, thing, offerer, venue) =>
  `${get(event, 'id', ' ')}/${get(thing, 'id', ' ')}/
   ${get(offerer, 'id', ' ')}/${get(venue, 'id', ' ')}`

const productKeys = [
  'ageMax',
  'ageMin',
  'condition',
  'description',
  'durationMinutes',
  'extraData',
  'isNational',
  'mediaUrls',
  'name',
  'type',
  'url',
]

export const selectFormInitialValuesByEventAndThingAndOfferAndOffererAndVenue = createCachedSelector(
  (state, event) => event,
  (state, event, thing) => thing,
  (state, event, thing, offer) => offer,
  (state, event, thing, offer, offerer) => offerer,
  (state, event, thing, offer, offerer, venue) => venue,
  (event, thing, offer, offerer, venue) => {
    const eventOrThing = event || thing || {}

    const formInitialValues = {}
    productKeys.forEach(key => {
      formInitialValues[key] = getValueFromOfferOrProduct(
        key,
        offer,
        eventOrThing
      )
    })

    return Object.assign(formInitialValues, {
      bookingEmail: get(offer, 'bookingEmail'),
      offererId: get(offerer, 'id'),
      venueId: get(venue, 'id'),
    })
  }
)(mapArgsToCacheKey)

export default selectFormInitialValuesByEventAndThingAndOfferAndOffererAndVenue
