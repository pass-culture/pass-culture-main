import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import { getValueFromOfferOrProduct } from './getValueFromOfferOrProduct'

const mapArgsToCacheKey = (state, product, offerer, venue) =>
  `${get(product, 'id', ' ')}/
   ${get(offerer, 'id', ' ')}/${get(venue, 'id', ' ')}`

const productKeys = [
  'ageMax',
  'ageMin',
  'condition',
  'description',
  'durationMinutes',
  'extraData',
  'isDuo',
  'isNational',
  'mediaUrls',
  'name',
  'type',
  'url',
]

const selectFormInitialValuesByProductAndOfferAndOffererAndVenue = createCachedSelector(
  (state, product) => product,
  (state, product, offer) => offer,
  (state, product, offer, offerer) => offerer,
  (state, product, offer, offerer, venue) => venue,
  (product, offer, offerer, venue) => {
    const formInitialValues = {}
    productKeys.forEach(key => {
      formInitialValues[key] = getValueFromOfferOrProduct(key, offer, product)
    })

    return Object.assign(formInitialValues, {
      bookingEmail: get(offer, 'bookingEmail'),
      offererId: get(offerer, 'id'),
      venueId: get(venue, 'id'),
    })
  }
)(mapArgsToCacheKey)

export default selectFormInitialValuesByProductAndOfferAndOffererAndVenue
