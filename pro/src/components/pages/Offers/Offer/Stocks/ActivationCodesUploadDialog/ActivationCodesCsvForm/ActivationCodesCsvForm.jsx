import PropTypes from 'prop-types'
import React, { Fragment, forwardRef } from 'react'

import Icon from 'components/layout/Icon'

import ActivationCodesUploadErrorDescription from './ActivationCodesUploadErrorDescription'
import ActivationCodesUploadInformationDescription from './ActivationCodesUploadInformationDescription'

export const ActivationCodeCsvForm = forwardRef(function ActivationCodeCsvForm(
  { isFileInputDisabled, submitThumbnail, errorMessage, fileName },
  ref
) {
  return (
    <Fragment>
      {errorMessage ? (
        <ActivationCodesUploadErrorDescription
          errorMessage={errorMessage}
          fileName={fileName}
        />
      ) : (
        <ActivationCodesUploadInformationDescription />
      )}

      <div className="activation-codes-upload-button-section">
        <label className="primary-button activation-codes-upload-label">
          Importer un fichier .csv depuis l’ordinateur{' '}
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
          <p>Format supporté : CSV</p>
          <p>Le poids du fichier ne doit pas dépasser 1 Mo</p>
        </div>
      </div>
      <div className="activation-codes-upload-separator" />
      <div className="activation-codes-upload-template-section">
        <p className="activation-codes-upload-gabarit">Gabarits</p>
        <p>
          <a
            className="quaternary-link"
            href={
              process.env.PUBLIC_URL +
              '/csvtemplates/CodesActivations-Gabarit.csv'
            }
            rel="noopener noreferrer"
            target="_blank"
            type="text/csv"
          >
            <Icon svg="ico-other-download" />
            <b>Gabarit CSV</b>{' '}
            <span className="activation-codes-upload-gabarit-type-and-size">
              (.csv, 50 ko)
            </span>
          </a>
        </p>
      </div>
    </Fragment>
  )
})

ActivationCodeCsvForm.defaultProps = {
  errorMessage: null,
}

ActivationCodeCsvForm.propTypes = {
  errorMessage: PropTypes.string,
  fileName: PropTypes.string.isRequired,
  isFileInputDisabled: PropTypes.bool.isRequired,
  submitThumbnail: PropTypes.func.isRequired,
}
