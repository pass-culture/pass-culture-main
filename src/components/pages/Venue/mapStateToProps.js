import selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity from './selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity'
import selectOffererById from 'selectors/selectOffererById'
import selectUserOffererByOffererIdAndUserIdAndRightsType from 'selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'

const mapStateToProps = (state, ownProps) => {
  const {
    currentUser,
    match: {
      params: { offererId, venueId },
    },
    query,
  } = ownProps
  const { id: currentUserId } = currentUser || {}
  const { isCreatedEntity } = query.context()

  const formInitialValues = selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity(
    state,
    venueId,
    offererId,
    isCreatedEntity
  )

  return {
    adminUserOfferer: selectUserOffererByOffererIdAndUserIdAndRightsType(
      state,
      offererId,
      currentUserId,
      'admin'
    ),
    formInitialValues,
    offerer: selectOffererById(state, offererId),
  }
}

export default mapStateToProps
