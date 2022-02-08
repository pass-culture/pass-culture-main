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
import { showNotification } from 'store/reducers/notificationReducer'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { selectVenueLabels } from 'store/selectors/data/venueLabelsSelectors'
import { selectVenueById } from 'store/selectors/data/venuesSelectors'
import { selectVenueTypes } from 'store/selectors/data/venueTypesSelectors'
import { offererNormalizer, venueNormalizer } from 'utils/normalizers'

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
      const body = formValues.isVirtual
        ? { businessUnitId: formValues.businessUnitId }
        : formatVenuePayload(formValues, false)
      dispatch(
        requestData({
          apiPath: `/venues/${venueId}`,
          body,
          handleFail,
          handleSuccess,
          method: 'PATCH',
          normalizer: venueNormalizer,
        })
      )
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
