import PropTypes from 'prop-types'
import React from 'react'

const PREVIEW_TEXT_MAX_LENGTH = 300

const OfferPreview = ({ formValues }) => {
  const buildPreviewText = previewText => {
    if (previewText.trim().length > PREVIEW_TEXT_MAX_LENGTH) {
      return previewText.substr(0, PREVIEW_TEXT_MAX_LENGTH) + '...'
    }
    return previewText
  }

  return (
    <div className="offer-preview">
      {(formValues.name || formValues.description) && (
        <div className="op-section">
          <div className="title-preview">
            {formValues.name}
          </div>
          <div className="op-section-description">
            {buildPreviewText(formValues.description)}
          </div>
        </div>
      )}
      {formValues.withdrawalDetails && (
        <div className="op-section">
          <div className="op-section-title">
            {'Modalités de retrait'}
          </div>
          <div className="op-section-description">
            {buildPreviewText(formValues.withdrawalDetails)}
          </div>
        </div>
      )}
    </div>
  )
}

OfferPreview.propTypes = {
  formValues: PropTypes.shape().isRequired,
}

export default OfferPreview
