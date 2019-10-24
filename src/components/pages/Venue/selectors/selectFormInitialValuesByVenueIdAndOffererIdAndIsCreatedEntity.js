import createCachedSelector from 're-reselect'
import { selectCurrentUser } from 'with-react-redux-login'

import { selectVenueById } from '../../../../selectors/data/venuesSelectors'

function mapArgsToCacheKey(state, venueId, offererId, isCreatedEntity) {
  return `${venueId || ''}/${offererId || ''}/${isCreatedEntity || ''}`
}

const selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity = createCachedSelector(
  selectVenueById,
  (state, venueId, offererId) => offererId,
  (state, venueId, offererId, isCreatedEntity) => isCreatedEntity,
  selectCurrentUser,
  (venue, offererId, isCreatedEntity, currentUser) => {
    const defaultData = {
      managingOffererId: offererId,
    }

    const formInitialValues = Object.assign(defaultData, venue)

    if (isCreatedEntity) {
      formInitialValues.bookingEmail = currentUser.email
    }

    return formInitialValues
  }
)(mapArgsToCacheKey)

export default selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity
