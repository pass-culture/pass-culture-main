import { connect } from 'react-redux'
import { compose } from 'redux'

import { withQueryRouter } from 'components/hocs/with-query-router/withQueryRouter'
import * as pcapi from 'repository/pcapi/pcapi'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import { formatVenuePayload } from '../utils/formatVenuePayload'
import VenueLabel from '../ValueObjects/VenueLabel'
import VenueType from '../ValueObjects/VenueType'

import VenueEdition from './VenueEdition'

export const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
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
    handleInitialRequest: async () => {
      const offererRequest = pcapi.getOfferer(offererId)
      const venueRequest = pcapi.getVenue(venueId)
      const venueTypesRequest = pcapi.getVenueTypes().then(venueTypes => {
        return venueTypes.map(type => new VenueType(type))
      })
      const venueLabelsRequest = pcapi.getVenueLabels().then(labels => {
        return labels.map(label => new VenueLabel(label))
      })

      const [offerer, venue, venueTypes, venueLabels] = await Promise.all([
        offererRequest,
        venueRequest,
        venueTypesRequest,
        venueLabelsRequest,
      ])

      return {
        offerer,
        venue,
        venueTypes,
        venueLabels,
      }
    },

    handleSubmitRequest: async ({ formValues, handleFail, handleSuccess }) => {
      const body = formValues.isVirtual
        ? { businessUnitId: formValues.businessUnitId }
        : formatVenuePayload(formValues, false)
      try {
        const response = await pcapi.editVenue(venueId, body)
        handleSuccess(response)
      } catch (responseError) {
        handleFail(responseError)
      }
    },

    handleSubmitRequestFail: ({ payload: { errors } }) => {
      let text = 'Une ou plusieurs erreurs sont présentes dans le formulaire.'
      if (errors.global) {
        text = `${text} ${errors.global[0]}`
      }

      dispatch(
        showNotification({
          text,
          type: 'error',
        })
      )
    },

    handleSubmitRequestSuccess: (_action, { hasDelayedUpdates }) => {
      const text = hasDelayedUpdates
        ? 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes'
        : 'Vos modifications ont bien été prises en compte'
      dispatch(
        showNotification({
          text,
          type: hasDelayedUpdates ? 'pending' : 'success',
        })
      )
    },
  }
}

export default compose(
  withQueryRouter(),
  connect(mapStateToProps, mapDispatchToProps)
)(VenueEdition)
