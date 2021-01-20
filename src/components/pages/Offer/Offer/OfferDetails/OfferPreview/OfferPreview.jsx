import PropTypes from 'prop-types'
import React from 'react'

const OfferPreview = ({ formValues }) => {
  return (
    <div className="offer-preview">
      <div className="category">
        <div className="title-preview">
          {formValues.name}
        </div>
        <div className="category-description">
          {formValues.description}
        </div>
      </div>
      <div className="category">
        <div className="category-title">
          {'Modalités de retrait'}
        </div>
        <div className="category-description">
          {formValues.withdrawalDetails}
        </div>
      </div>
    </div>
  )
}

OfferPreview.propTypes = {
  formValues: PropTypes.shape().isRequired,
}

export default OfferPreview
