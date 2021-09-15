/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { WEBAPP_URL_NEW, WEBAPP_URL_OLD } from 'utils/config'

import useActiveFeature from '../../../../hooks/useActiveFeature'

const getOfferPreviewUrl = (offerId, mediationId, isWebappV2Enabled) => {
  const baseUrl = isWebappV2Enabled ? WEBAPP_URL_NEW : WEBAPP_URL_OLD
  const webappOfferUrl = isWebappV2Enabled
    ? `${baseUrl}/offre/${offerId}`
    : `${baseUrl}/offre/details/${offerId}`

  return mediationId ? `${webappOfferUrl}/${mediationId}` : webappOfferUrl
}

const OfferPreviewLink = ({ offerId, mediationId }) => {
  const isWebappV2Enabled = useActiveFeature('WEBAPP_V2_ENABLED')
  const offerPreviewUrl = getOfferPreviewUrl(offerId, mediationId, isWebappV2Enabled)

  const openWindow = useCallback(
    event => {
      event.preventDefault()

      window.open(offerPreviewUrl, 'targetWindow', 'toolbar=no,width=375,height=667').focus()
    },
    [offerPreviewUrl]
  )

  return (
    <a
      className="secondary-link"
      href={offerPreviewUrl}
      onClick={openWindow}
      rel="noopener noreferrer"
      target="_blank"
    >
      Prévisualiser dans l’app
    </a>
  )
}

OfferPreviewLink.defaultProps = {
  mediationId: null,
}

OfferPreviewLink.propTypes = {
  mediationId: PropTypes.string,
  offerId: PropTypes.string.isRequired,
}

export default OfferPreviewLink
