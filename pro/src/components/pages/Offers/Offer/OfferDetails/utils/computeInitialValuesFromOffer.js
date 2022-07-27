import { DEFAULT_FORM_VALUES } from '../_constants'
import {
  checkHasNoDisabilityCompliance,
  getAccessibilityValues,
} from '../OfferForm/AccessibilityCheckboxList'

const computeInitialValuesFromOffer = (offer, subCategories) => {
  if (!offer || !subCategories) {
    return {}
  }

  let initialValues = Object.keys(DEFAULT_FORM_VALUES).reduce((acc, field) => {
    if (field in offer && offer[field] !== null) {
      return { ...acc, [field]: offer[field] }
    } else if (offer.extraData && field in offer.extraData) {
      return { ...acc, [field]: offer.extraData[field] }
    }
    return { ...acc, [field]: DEFAULT_FORM_VALUES[field] }
  }, {})

  const offerAccessibility = getAccessibilityValues(offer)
  const venueAccessibility = getAccessibilityValues(offer.venue)
  if (
    Object.values(offerAccessibility).includes(null) &&
    !Object.values(venueAccessibility).includes(null)
  ) {
    initialValues = { ...initialValues, ...venueAccessibility }
  }

  initialValues.categoryId = subCategories.find(
    subCategory => subCategory.id === offer.subcategoryId
  ).categoryId

  initialValues.subcategoryId = offer.subcategoryId
  initialValues.offererId = offer.venue.managingOffererId
  initialValues.noDisabilityCompliant = checkHasNoDisabilityCompliance(offer)

  return initialValues
}

export default computeInitialValuesFromOffer
