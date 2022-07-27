import PropTypes from 'prop-types'
import React, { useEffect, useMemo, useState } from 'react'

import { VenueDetails } from 'components/pages/Offers/Offer/OfferDetails/OfferPreview/VenueDetails'
import { ReactComponent as DuoSvg } from 'icons/ico-duo.svg'
import { ReactComponent as PassCultureSvg } from 'icons/ico-passculture.svg'
import { ReactComponent as TagSvg } from 'icons/ico-tag.svg'
import * as pcapi from 'repository/pcapi/pcapi'

const PREVIEW_TEXT_MAX_LENGTH = 300

const OfferPreview = ({ offerPreviewData }) => {
  const [venue, setVenue] = useState(null)

  const buildPreviewText = previewText => {
    if (previewText.trim().length > PREVIEW_TEXT_MAX_LENGTH) {
      return `${previewText.substr(0, PREVIEW_TEXT_MAX_LENGTH)}...`
    }
    return previewText
  }

  useEffect(() => {
    async function changeVenue() {
      setVenue(await pcapi.getVenue(offerPreviewData.venueId))
    }
    offerPreviewData.venueId ? changeVenue() : setVenue(null)
  }, [offerPreviewData.venueId])

  const isDuoEnabled = useMemo(
    () => offerPreviewData.isEvent && offerPreviewData.isDuo,
    [offerPreviewData.isDuo, offerPreviewData.isEvent]
  )

  return (
    <div className="offer-preview" data-testid="offer-preview-section">
      <div className="op-section">
        {offerPreviewData.name && (
          <div className="title-preview">{offerPreviewData.name}</div>
        )}
        <div className="op-options-summary">
          <div className="op-option">
            <PassCultureSvg aria-hidden className="op-option-ico" />
            <span className="op-option-text">Type</span>
          </div>

          <div className={`op-option${!isDuoEnabled ? ' disabled' : ''}`}>
            <DuoSvg aria-hidden className="op-option-ico" />
            <span className="op-option-text">À deux !</span>
          </div>

          <div className="op-option">
            <TagSvg aria-hidden className="op-option-ico" />
            <span className="op-option-text">- - €</span>
          </div>
        </div>
        {offerPreviewData.description && (
          <div className="op-section-text">
            {buildPreviewText(offerPreviewData.description)}
          </div>
        )}
      </div>

      {venue && (
        <div>{!venue.isVirtual && <VenueDetails physicalVenue={venue} />}</div>
      )}

      {offerPreviewData.withdrawalDetails && (
        <div className="op-section">
          <div className="op-section-title">Modalités de retrait</div>
          <div className="op-section-text">
            {buildPreviewText(offerPreviewData.withdrawalDetails)}
          </div>
        </div>
      )}
    </div>
  )
}

OfferPreview.propTypes = {
  offerPreviewData: PropTypes.shape({
    description: PropTypes.string,
    isEvent: PropTypes.bool,
    isDuo: PropTypes.bool,
    name: PropTypes.string,
    venueId: PropTypes.string,
    withdrawalDetails: PropTypes.string,
  }).isRequired,
}

export default OfferPreview
