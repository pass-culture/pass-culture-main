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
      params: { offererId },
    },
    query,
    venue,
  } = ownProps
  const { id: venueId } = venue || {}
  return {
    handleInitialRequest: () => {
      dispatch(
        requestData({
          apiPath: `/offerers/${offererId}`,
          handleSuccess: () => {
            if (!venueId) {
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
      const context = query.context({ id: venueId })
      const { isCreatedEntity, method } = context
      const apiPath = `/venues/${venueId || ''}`

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
      const venueId = datum.id
      const createOfferPathname = `/offres/${CREATION}?lieu=${venueId}`
      const text =
        method === 'POST' ? (
          <p>
            Lieu créé. Vous pouvez maintenant y{' '}
            <NavLink
              to={createOfferPathname}
              onClick={() => dispatch(closeNotification())}>
              créer une offre
            </NavLink>
            , ou en importer automatiquement.
          </p>
        ) : (
          'Lieu modifié avec succès !'
        )

      dispatch(
        showNotification({
          text,
          type: 'success',
        })
      )
      // TODO: do it in the way that the notification
      // is displayed in the next page an disappear when
      // the user is after changing to another page
    },
  }
}

export default mapDispatchToProps
