import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { WEBAPP_URL } from 'utils/config'

const OfferPreviewLink = ({ nonHumanizedId }) => {
  const offerPreviewUrl = `${WEBAPP_URL}/offre/${nonHumanizedId}`

  const openWindow = useCallback(
    event => {
      event.preventDefault()

      window
        .open(
          offerPreviewUrl,
          'targetWindow',
          'toolbar=no,width=375,height=667'
        )
        .focus()
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

OfferPreviewLink.propTypes = {
  nonHumanizedId: PropTypes.number.isRequired,
}

export default OfferPreviewLink
