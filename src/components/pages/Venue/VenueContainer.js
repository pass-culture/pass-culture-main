import { closeNotification, showNotification } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import React from 'react'
import { NavLink } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import Venue from './Venue'
import selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity from './selectors/selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity'
import { VENUE_CREATION_PATCH_KEYS, VENUE_MODIFICATION_PATCH_KEYS } from './utils/utils'
import { withRequiredLogin } from '../../hocs'
import { CREATION } from '../../hocs/withFrenchQueryRouter'
import selectUserOffererByOffererIdAndUserIdAndRightsType from '../../../selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'
import selectOffererById from '../../../selectors/selectOffererById'
import { offererNormalizer, venueNormalizer } from '../../../utils/normalizers'
import { formatPatch } from '../../../utils/formatPatch'

const handleOnClick = dispatch => () => dispatch(closeNotification())

export const mapStateToProps = (state, ownProps) => {
  const {
    currentUser,
    match: {
      params: { offererId, venueId },
    },
    query,
  } = ownProps
  const { id: currentUserId } = currentUser
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

export const mapDispatchToProps = (dispatch, ownProps) => {
  const {
    match: {
      params: { offererId, venueId },
    },
    query,
  } = ownProps
  const { isCreatedEntity, method } = query.context({ id: venueId })

  const buildNotificationMessage = (venueId, method) => {
    const isVenueCreated = method === 'POST'

    if (isVenueCreated) {
      const createOfferPathname = `/offres/${CREATION}?lieu=${venueId}`

      return (
        <p>
          {'Lieu créé. Vous pouvez maintenant y '}
          <NavLink
            onClick={handleOnClick(dispatch)}
            to={createOfferPathname}
          >
            {'créer une offre'}
          </NavLink>
          {', ou en importer automatiquement. '}
        </p>
      )
    }
    return 'Lieu modifié avec succès !'
  }

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
      const apiPath = `/venues/${isCreatedEntity ? '' : venueId}`

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
          method,
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
      const notificationMessage = buildNotificationMessage(datum.id, method)
      dispatch(
        showNotification({
          text: notificationMessage,
          type: 'success',
        })
      )
    },
  }
}

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Venue)
