/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { WEBAPP_URL_NEW } from 'utils/config'

const OfferPreviewLink = ({ nonHumanizedOfferId }) => {
  const offerPreviewUrl = `${WEBAPP_URL_NEW}/offre/${nonHumanizedOfferId}`

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
  nonHumanizedOfferId: PropTypes.number.isRequired,
}

export default OfferPreviewLink
