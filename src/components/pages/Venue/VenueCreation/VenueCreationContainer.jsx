import { showNotification } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import VenueCreation from './VenueCreation'
import NotificationMessage from '../Notification'

import { withRequiredLogin } from '../../../hocs'
import withTracking from '../../../hocs/withTracking'
import { CREATION } from '../../../hocs/withFrenchQueryRouter'
import { VENUE_CREATION_PATCH_KEYS, VENUE_MODIFICATION_PATCH_KEYS } from '../utils/utils'
import { offererNormalizer, venueNormalizer } from '../../../../utils/normalizers'
import { formatPatch } from '../../../../utils/formatPatch'
import { selectUserOffererByOffererIdAndUserIdAndRightsType } from '../../../../selectors/data/userOfferersSelectors'
import { selectOffererById } from '../../../../selectors/data/offerersSelectors'
import selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity from '../selectors/selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity'

export const mapStateToProps = (state, ownProps) => {
  const {
    currentUser,
    match: {
      params: { offererId, venueId },
    },
  } = ownProps
  const { id: currentUserId } = currentUser
  const isCreatedEntity = true
  const formInitialValues = selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity(
    state,
    venueId,
    offererId,
    isCreatedEntity
  )
  const adminUserOfferer = selectUserOffererByOffererIdAndUserIdAndRightsType(
    state,
    offererId,
    currentUserId,
    'admin'
  )

  return {
    adminUserOfferer,
    formInitialValues,
    offerer: selectOffererById(state, offererId),
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  const {
    match: {
      params: { offererId, venueId },
    },
  } = ownProps

  return {
    handleInitialRequest: () => {
      dispatch(
        requestData({
          apiPath: `/offerers/${offererId}`,
          handleSuccess: () => {
            if (!venueId || venueId === CREATION) {
              return
            }
            dispatch(
              requestData({
                apiPath: `/venues/${venueId}`,
                normalizer: venueNormalizer,
              })
            )
          },
          normalizer: offererNormalizer,
        })
      )
      dispatch(requestData({ apiPath: `/userOfferers/${offererId}` }))
    },

    handleSubmitRequest: ({ formValues, handleFail, handleSuccess }) => {
      const apiPath = '/venues/'
      const isCreatedEntity = true

      const body = formatPatch(
        formValues,
        { isCreatedEntity },
        VENUE_CREATION_PATCH_KEYS,
        VENUE_MODIFICATION_PATCH_KEYS
      )

      dispatch(
        requestData({
          apiPath,
          body,
          handleFail,
          handleSuccess,
          method: 'POST',
          normalizer: venueNormalizer,
        })
      )
    },

    handleSubmitRequestFail: (state, action) => {
      const {
        payload: { errors },
      } = action

      let text = 'Formulaire non validé.'
      if (errors.global) {
        text = `${text} ${errors.global[0]}`
      }

      dispatch(
        showNotification({
          text,
          type: 'danger',
        })
      )
    },

    handleSubmitRequestSuccess: (state, action) => {
      const {
        config: { method },
        payload: { datum },
      } = action

      const informationsDisplayed = {
        venueId: datum.id,
        offererId,
        dispatch,
      }
      let notificationMessage = 'Lieu modifié avec succès !'
      if (method == 'POST') {
        notificationMessage = NotificationMessage(informationsDisplayed)
      }

      dispatch(
        showNotification({
          text: notificationMessage,
          type: 'success',
        })
      )
    },
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackCreateVenue: createdVenueId => {
      ownProps.tracking.trackEvent({ action: 'createVenue', name: createdVenueId })
    },
  }
}

export default compose(
  withTracking('Venue'),
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(VenueCreation)
