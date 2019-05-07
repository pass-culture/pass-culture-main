import { closeNotification, showNotification } from 'pass-culture-shared'
import React from 'react'
import { NavLink } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import {
  VENUE_MODIFICATION_PATCH_KEYS,
  VENUE_CREATION_PATCH_KEYS,
} from './utils'
import { CREATION } from 'components/hocs/withFrenchQueryRouter'
import { formatPatch } from 'utils/formatPatch'
import { offererNormalizer, venueNormalizer } from 'utils/normalizers'

const mapDispatchToProps = (dispatch, ownProps) => {
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
          Lieu créé. Vous pouvez maintenant y{' '}
          <NavLink
            to={createOfferPathname}
            onClick={() => dispatch(closeNotification())}>
            créer une offre
          </NavLink>
          , ou en importer automatiquement.
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

export default mapDispatchToProps
