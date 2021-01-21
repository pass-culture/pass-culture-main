import PropTypes from 'prop-types'
import React from 'react'

const OfferPreview = ({ formValues }) => {
  const buildPreviewText = previewText => {
    if (previewText.length > 300) {
      return previewText.substr(0, 300) + '...'
    }
    return previewText
  }

  return (
    <div className="offer-preview">
      {(formValues.name || formValues.description) && (
        <div className="category">
          <div className="title-preview">
            {formValues.name}
          </div>
          <div className="category-description">
            {buildPreviewText(formValues.description)}
          </div>
        </div>
      )}
      {formValues.withdrawalDetails && (
        <div className="category">
          <div className="category-title">
            {'Modalités de retrait'}
          </div>
          <div className="category-description">
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
