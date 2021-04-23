import PropTypes from 'prop-types'
import React, { useEffect, useMemo, useState } from 'react'

import { ReactComponent as DuoSvg } from 'icons/ico-duo.svg'
import { ReactComponent as PassCultureSvg } from 'icons/ico-passculture.svg'
import { ReactComponent as TagSvg } from 'icons/ico-tag.svg'
import * as pcapi from 'repository/pcapi/pcapi'

const PREVIEW_TEXT_MAX_LENGTH = 300

const OfferPreview = ({ formValues, offerType }) => {
  const [venue, setVenue] = useState(null)

  const buildPreviewText = previewText => {
    if (previewText.trim().length > PREVIEW_TEXT_MAX_LENGTH) {
      return previewText.substr(0, PREVIEW_TEXT_MAX_LENGTH) + '...'
    }
    return previewText
  }

  useEffect(() => {
    formValues.venueId
      ? pcapi.getVenue(formValues.venueId).then(venue => {
        setVenue(venue)
      })
      : setVenue(null)
  }, [formValues.venueId])

  const venueName = useMemo(() => venue?.publicName || venue?.name, [venue])
  const isDuoEnabled = useMemo(() => offerType && offerType.type === 'Event' && formValues.isDuo, [
    formValues.isDuo,
    offerType,
  ])

  return (
    <div
      className="offer-preview"
      data-testid="offer-preview-section"
    >
      <div className="op-section">
        {formValues.name && (
          <div className="title-preview">
            {formValues.name}
          </div>
        )}
        <div className="op-options-summary">
          <div className="op-option">
            <PassCultureSvg
              aria-hidden
              className="op-option-ico"
            />
            <span className="op-option-text">
              {'Type'}
            </span>
          </div>

          <div className={`op-option${!isDuoEnabled ? ' disabled' : ''}`}>
            <DuoSvg
              aria-hidden
              className="op-option-ico"
            />
            <span className="op-option-text">
              {'À deux !'}
            </span>
          </div>

          <div className="op-option">
            <TagSvg
              aria-hidden
              className="op-option-ico"
            />
            <span className="op-option-text">
              {'- - €'}
            </span>
          </div>
        </div>
        {formValues.description && (
          <div className="op-section-text">
            {buildPreviewText(formValues.description)}
          </div>
        )}
      </div>

      {venue && !venue.isVirtual && (
        <div className="op-section">
          <div className="op-section-title">
            {'Où ?'}
          </div>
          <div className="op-section-secondary-title">
            {'Adresse'}
          </div>
          <div className="op-section-text op-address">
            {`${venueName} - ${venue.address} - ${venue.postalCode} - ${venue.city}`}
          </div>
          <div className="op-section-secondary-title">
            {'Distance'}
          </div>
          <div className="op-section-text">
            {'- - km'}
          </div>
        </div>
      )}

      {formValues.withdrawalDetails && (
        <div className="op-section">
          <div className="op-section-title">
            {'Modalités de retrait'}
          </div>
          <div className="op-section-text">
            {buildPreviewText(formValues.withdrawalDetails)}
          </div>
        </div>
      )}
    </div>
  )
}

OfferPreview.defaultProps = {
  offerType: {},
}

OfferPreview.propTypes = {
  formValues: PropTypes.shape().isRequired,
  offerType: PropTypes.shape(),
}

export default OfferPreview
