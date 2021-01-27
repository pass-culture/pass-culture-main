import PropTypes from 'prop-types'
import React from 'react'

import { ReactComponent as DuoSvg } from 'icons/ico-duo.svg'
import { ReactComponent as PassCultureSvg } from 'icons/ico-passculture.svg'
import { ReactComponent as TagSvg } from 'icons/ico-tag.svg'

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

          <div className={`op-option${!formValues.isDuo ? ' disabled' : ''}`}>
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

OfferPreview.propTypes = {
  formValues: PropTypes.shape().isRequired,
}

export default OfferPreview
