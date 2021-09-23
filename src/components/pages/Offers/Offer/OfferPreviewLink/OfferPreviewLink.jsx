/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { WEBAPP_URL_NEW, WEBAPP_URL_OLD } from 'utils/config'

import useActiveFeature from '../../../../hooks/useActiveFeature'

const OfferPreviewLink = ({ offerId, nonHumanizedOfferId, mediationId }) => {
  const isWebappV2Enabled = useActiveFeature('WEBAPP_V2_ENABLED')
  const webappOfferUrl = isWebappV2Enabled
    ? `${WEBAPP_URL_NEW}/offre/${nonHumanizedOfferId}`
    : `${WEBAPP_URL_OLD}/offre/details/${offerId}`

  const offerPreviewUrl = mediationId ? `${webappOfferUrl}/${mediationId}` : webappOfferUrl

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
  nonHumanizedOfferId: PropTypes.number.isRequired,
  offerId: PropTypes.string.isRequired,
}

export default OfferPreviewLink
