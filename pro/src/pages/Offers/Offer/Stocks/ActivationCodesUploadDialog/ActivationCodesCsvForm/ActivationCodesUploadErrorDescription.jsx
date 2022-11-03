import PropTypes from 'prop-types'
import React from 'react'

const ActivationCodesUploadErrorDescription = ({ fileName, errorMessage }) => {
  return (
    <div className="activation-codes-upload-description">
      <p>
        Une erreur s’est produite lors de l’import de votre fichier{' '}
        <b>{fileName}</b>.
      </p>
      <p>{errorMessage}</p>
      <p>Veuillez réessayer.</p>
    </div>
  )
}

ActivationCodesUploadErrorDescription.propTypes = {
  errorMessage: PropTypes.string.isRequired,
  fileName: PropTypes.string.isRequired,
}

export default ActivationCodesUploadErrorDescription
