import { showNotification } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { offererNormalizer, venueNormalizer } from '../../../../utils/normalizers'
import { withRequiredLogin } from '../../../hocs'
import { CREATION } from '../../../hocs/withFrenchQueryRouter'
import withTracking from '../../../hocs/withTracking'
import NotificationMessage from '../Notification'
import VenueCreation from './VenueCreation'
import { selectVenueTypes } from 'store/selectors/data/venueTypesSelectors'
import VenueType from '../ValueObjects/VenueType'
import { formatVenuePayload } from '../utils/formatVenuePayload'
import VenueLabel from '../ValueObjects/VenueLabel'
import { selectVenueLabels } from 'store/selectors/data/venueLabelsSelectors'

export const mapStateToProps = (
  state,
  {
    currentUser,
    match: {
      params: { offererId },
    },
  }
) => ({
  venueTypes: selectVenueTypes(state).map(type => new VenueType(type)),
  venueLabels: selectVenueLabels(state).map(label => new VenueLabel(label)),
  formInitialValues: {
    managingOffererId: offererId,
    bookingEmail: currentUser.email,
  },
  offerer: selectOffererById(state, offererId),
})

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
      dispatch(requestData({ apiPath: `/venue-types` }))
      dispatch(requestData({ apiPath: `/venue-labels` }))
    },

    handleSubmitRequest: ({ formValues, handleFail, handleSuccess }) => {
      const apiPath = '/venues/'

      const body = formatVenuePayload(formValues, true)

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
      let notificationMessage = 'Lieu créé avec succès !'
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
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(VenueCreation)
