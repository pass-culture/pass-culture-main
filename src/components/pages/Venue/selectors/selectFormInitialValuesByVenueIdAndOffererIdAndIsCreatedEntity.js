import createCachedSelector from 're-reselect'

import selectVenueById from '../../../../selectors/selectVenueById'

function mapArgsToCacheKey(state, venueId, offererId, isCreatedEntity) {
  return `${venueId || ''}/${offererId || ''}/${isCreatedEntity || ''}`
}

const selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity = createCachedSelector(
  selectVenueById,
  (state, venueId, offererId) => offererId,
  (state, venueId, offererId, isCreatedEntity) => isCreatedEntity,
  state => state.user && state.user.email,
  (venue, offererId, isCreatedEntity, bookingEmail) => {
    const defaultData = {
      managingOffererId: offererId,
    }

    const formInitialValues = Object.assign(defaultData, venue)

    if (isCreatedEntity) {
      formInitialValues.bookingEmail = bookingEmail
    }

    return formInitialValues
  }
)(mapArgsToCacheKey)

export default selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity
