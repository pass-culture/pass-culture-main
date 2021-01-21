import PropTypes from 'prop-types'
import React from 'react'

const OfferPreview = ({ formValues }) => {
  const buildDescriptionPreview = () => {
    const description = formValues.description
    if (description.length > 300) {
      return description.substr(0, 300) + '...'
    }
    return description
  }

  const buildWithdrawalDetailsPreview = () => {
    const withdrawalDetails = formValues.withdrawalDetails
    if (withdrawalDetails.length > 300) {
      return withdrawalDetails.substr(0, 300) + '...'
    }
    return withdrawalDetails
  }

  return (
    <div className="offer-preview">
      {(formValues.name || formValues.description) && (
        <div className="category">
          <div className="title-preview">
            {formValues.name}
          </div>
          <div className="category-description">
            {buildDescriptionPreview()}
          </div>
        </div>
      )}
      {formValues.withdrawalDetails && (
        <div className="category">
          <div className="category-title">
            {'Modalités de retrait'}
          </div>
          <div className="category-description">
            {buildWithdrawalDetailsPreview()}
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
