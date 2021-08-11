import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { IS_PROD, WEBAPP_URL } from 'utils/config'

const webappOfferUrl = (offerId, mediationId) => {
  const webappUrl = IS_PROD ? WEBAPP_URL : 'http://localhost:3000'
  const urlWithOfferId = `${webappUrl}/offre/details/${offerId}`

  return mediationId ? `${urlWithOfferId}/${mediationId}` : urlWithOfferId
}

const OfferPreviewLink = ({ offerId, mediationId }) => {
  const offerWebappUrl = webappOfferUrl(offerId, mediationId)

  const openWindow = useCallback(
    event => {
      event.preventDefault()

      window.open(offerWebappUrl, 'targetWindow', 'toolbar=no,width=375,height=667').focus()
    },
    [offerWebappUrl]
  )

  return (
    <a
      className="secondary-link"
      href={offerWebappUrl}
      onClick={openWindow}
      rel="noopener noreferrer"
      target="_blank"
    >
      {'Prévisualiser dans l’app'}
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
