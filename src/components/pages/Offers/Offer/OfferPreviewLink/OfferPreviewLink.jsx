import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { WEBAPP_URL } from 'utils/config'

const getOfferPreviewUrl = (offerId, mediationId) => {
  const webappOfferUrl = `${WEBAPP_URL}/offre/details/${offerId}`

  return mediationId ? `${webappOfferUrl}/${mediationId}` : webappOfferUrl
}

const OfferPreviewLink = ({ offerId, mediationId }) => {
  const offerPreviewUrl = getOfferPreviewUrl(offerId, mediationId)

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
