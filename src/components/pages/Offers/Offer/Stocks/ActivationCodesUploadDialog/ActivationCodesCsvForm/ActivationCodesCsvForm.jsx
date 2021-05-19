import PropTypes from 'prop-types'
import React, { forwardRef, Fragment } from 'react'

import ActivationCodesUploadErrorDescription from './ActivationCodesUploadErrorDescription'
import ActivationCodesUploadInformationDescription from './ActivationCodesUploadInformationDescription'

export const ActivationCodeCsvForm = forwardRef(function ActivationCodeCsvForm(
  { isFileInputDisabled, submitThumbnail, errorMessage },
  ref
) {
  return (
    <Fragment>
      {errorMessage ? (
        <ActivationCodesUploadErrorDescription
          errorMessage={errorMessage}
          fileName={ref.current.files[0].name}
        />
      ) : (
        <ActivationCodesUploadInformationDescription />
      )}

      <div className="activation-codes-upload-button-section">
        <label className="primary-button activation-codes-upload-label">
          {'Importer un fichier .csv depuis l’ordinateur'}
          <input
            accept=".csv"
            className="activation-codes-upload-input"
            disabled={isFileInputDisabled}
            onChange={submitThumbnail}
            ref={ref}
            type="file"
          />
        </label>
        <div className="activation-codes-upload-button-caption">
          <p>
            {'Format supporté : CSV'}
          </p>
          <p>
            {'Le poids du fichier ne doit pas dépasser 1 Mo'}
          </p>
        </div>
      </div>
      <div className="activation-codes-upload-separator" />
    </Fragment>
  )
})

ActivationCodeCsvForm.defaultProps = {
  errorMessage: null,
}

ActivationCodeCsvForm.propTypes = {
  errorMessage: PropTypes.string,
  isFileInputDisabled: PropTypes.bool.isRequired,
  submitThumbnail: PropTypes.func.isRequired,
}
