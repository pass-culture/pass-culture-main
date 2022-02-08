/*
 * @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt deprecated "Gaël: deprecated usage of redux-saga-data"
 * @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
 * @debt deprecated "Gaël: deprecated usage of withQueryRouter"
 */

import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { withQueryRouter } from 'components/hocs/with-query-router/withQueryRouter'
import { CREATION } from 'components/hocs/withFrenchQueryRouter'
import { isFeatureActive } from 'store/features/selectors'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { selectVenueLabels } from 'store/selectors/data/venueLabelsSelectors'
import { selectVenueTypes } from 'store/selectors/data/venueTypesSelectors'
import { offererNormalizer, venueNormalizer } from 'utils/normalizers'

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
    venueTypes: selectVenueTypes(state).map(type => new VenueType(type)),
    venueLabels: selectVenueLabels(state).map(label => new VenueLabel(label)),
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
  }
}

export default compose(
  withQueryRouter(),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(VenueCreation)
