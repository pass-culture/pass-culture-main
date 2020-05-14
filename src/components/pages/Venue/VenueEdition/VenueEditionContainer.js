import { showNotification } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'
import { selectOffererById } from '../../../../selectors/data/offerersSelectors'
import { selectVenueById } from '../../../../selectors/data/venuesSelectors'
import { offererNormalizer, venueNormalizer } from '../../../../utils/normalizers'
import { withRequiredLogin } from '../../../hocs'
import withTracking from '../../../hocs/withTracking'
import VenueEdition from './VenueEdition'
import { selectVenueTypes } from '../../../../selectors/data/venueTypesSelectors'
import VenueType from '../ValueObjects/VenueType'
import { formatVenuePayload } from '../utils/formatVenuePayload'
import { selectVenueLabels } from '../../../../selectors/data/venueLabelsSelectors'
import VenueLabel from '../ValueObjects/VenueLabel'

export const mapStateToProps = (
  state,
  {
    match: {
      params: { offererId, venueId },
    },
  }
) => ({
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
        showNotification({
          text,
          type: 'danger',
        })
      )
    },

    handleSubmitRequestSuccess: () => {
      dispatch(
        showNotification({
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
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(VenueEdition)
