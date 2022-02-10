import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import { withQueryRouter } from 'components/hocs/with-query-router/withQueryRouter'
import * as pcapi from 'repository/pcapi/pcapi'
import { isFeatureActive } from 'store/features/selectors'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import NotificationMessage from '../Notification'
import { formatVenuePayload } from '../utils/formatVenuePayload'
import VenueLabel from '../ValueObjects/VenueLabel'
import VenueType from '../ValueObjects/VenueType'

import VenueCreation from './VenueCreation'

export const mapStateToProps = (state, ownProps) => {
  const {
    match: {
      params: { offererId },
    },
  } = ownProps

  const currentUser = selectCurrentUser(state)
  return {
    currentUser: currentUser,
    formInitialValues: {
      managingOffererId: offererId,
      bookingEmail: currentUser.email,
    },
    offerer: selectOffererById(state, offererId),
    isBankInformationWithSiretActive: isFeatureActive(
      state,
      'ENFORCE_BANK_INFORMATION_WITH_SIRET'
    ),
    isEntrepriseApiDisabled: isFeatureActive(state, 'DISABLE_ENTERPRISE_API'),
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  const {
    match: {
      params: { offererId },
    },
  } = ownProps

  return {
    handleInitialRequest: async () => {
      const offererRequest = pcapi.getOfferer(offererId)
      const venueTypesRequest = pcapi.getVenueTypes().then(venueTypes => {
        return venueTypes.map(type => new VenueType(type))
      })
      const venueLabelsRequest = pcapi.getVenueLabels().then(labels => {
        return labels.map(label => new VenueLabel(label))
      })
      const [offerer, venueTypes, venueLabels] = await Promise.all([
        offererRequest,
        venueTypesRequest,
        venueLabelsRequest,
      ])
      return {
        offerer,
        venueTypes,
        venueLabels,
      }
    },

    handleSubmitRequest: async ({ formValues, handleFail, handleSuccess }) => {
      const body = formatVenuePayload(formValues, true)

      try {
        const response = await pcapi.createVenue(body)
        handleSuccess(response)
      } catch (responseError) {
        handleFail(responseError)
      }
    },

    handleSubmitFailNotification: errors => {
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

    handleSubmitSuccessNotification: payload => {
      const notificationMessageProps = {
        venueId: payload.id,
        offererId,
      }

      dispatch(
        showNotification({
          text: <NotificationMessage {...notificationMessageProps} />,
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
  }
}

export default compose(
  withQueryRouter(),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(VenueCreation)
