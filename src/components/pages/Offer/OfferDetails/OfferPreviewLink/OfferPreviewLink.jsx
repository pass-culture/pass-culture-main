import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import Icon from 'components/layout/Icon'
import { IS_PROD } from 'utils/config'

const webappOfferUrl = (offerId, mediationId = undefined) => {
  const webappUrl = IS_PROD
    ? window.location.href.split('offres')[0].replace('pro', 'app')
    : 'http://localhost:3000/'
  const urlWithOfferId = `${webappUrl}offre/details/${offerId}`

  return mediationId ? `${urlWithOfferId}/${mediationId}` : urlWithOfferId
}

const OfferPreviewLink = ({ offerId, mediationId }) => {
  const offerWebappUrl = webappOfferUrl(offerId, mediationId)
  const onClick = useCallback(
    event => {
      event.preventDefault()
      window.open(offerWebappUrl, 'targetWindow', 'toolbar=no,width=375,height=667').focus()
    },
    [offerWebappUrl]
  )

  return (
    <a
      className="link"
      href={offerWebappUrl}
      onClick={onClick}
      rel="noopener noreferrer"
      target="_blank"
    >
      <span
        data-place="bottom"
        data-testid="offer-preview-link-tooltip"
        data-tip="Ouvrir un nouvel onglet avec la prévisualisation de l’offre."
        data-type="info"
      >
        <Icon
          data-testid="offer-preview-link-icon"
          svg="ico-eye"
        />
      </span>
      {'Prévisualiser'}
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
