import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'
import withQueryRouter from 'with-query-router'

import withTracking from 'components/hocs/withTracking'
import { showNotificationV1 } from 'store/reducers/notificationReducer'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { selectVenueLabels } from 'store/selectors/data/venueLabelsSelectors'
import { selectVenueById } from 'store/selectors/data/venuesSelectors'
import { selectVenueTypes } from 'store/selectors/data/venueTypesSelectors'

import { offererNormalizer, venueNormalizer } from '../../../../utils/normalizers'
import { formatVenuePayload } from '../utils/formatVenuePayload'
import VenueLabel from '../ValueObjects/VenueLabel'
import VenueType from '../ValueObjects/VenueType'

import VenueEdition from './VenueEdition'

export const mapStateToProps = (
  state,
  {
    match: {
      params: { offererId, venueId },
    },
  }
) => ({
  currentUser: selectCurrentUser(state),
  venueTypes: selectVenueTypes(state).map(type => new VenueType(type)),
  venueLabels: selectVenueLabels(state).map(label => new VenueLabel(label)),
  venue: selectVenueById(state, venueId),
  offerer: selectOffererById(state, offererId),
})

export const mapDispatchToProps = (
  dispatch,
  {
    match: {
      params: { offererId, venueId },
    },
  }
) => {
  return {
    handleInitialRequest: () => {
      dispatch(
        requestData({
          apiPath: `/offerers/${offererId}`,
          handleSuccess: () => {
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
      const body = formatVenuePayload(formValues, false)

      dispatch(
        requestData({
          apiPath: `/venues/${venueId}`,
          body: body,
          handleFail,
          handleSuccess,
          method: 'PATCH',
          normalizer: venueNormalizer,
        })
      )
    },

    handleSubmitRequestFail: ({ payload: { errors } }) => {
      let text = 'Formulaire non validé.'
      if (errors.global) {
        text = `${text} ${errors.global[0]}`
      }

      dispatch(
        showNotificationV1({
          text,
          type: 'danger',
        })
      )
    },

    handleSubmitRequestSuccess: () => {
      dispatch(
        showNotificationV1({
          text: 'Lieu modifié avec succès !',
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
    trackModifyVenue: venueId => {
      ownProps.tracking.trackEvent({ action: 'modifyVenue', name: venueId })
    },
  }
}

export default compose(
  withTracking('Venue'),
  withQueryRouter(),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(VenueEdition)
