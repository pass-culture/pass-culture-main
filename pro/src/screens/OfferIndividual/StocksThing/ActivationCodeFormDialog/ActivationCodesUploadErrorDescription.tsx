import React from 'react'
interface IActivationCodesUploadErrorDescription {
  fileName: string
  errorMessage: string
}

const ActivationCodesUploadErrorDescription = ({
  fileName,
  errorMessage,
}: IActivationCodesUploadErrorDescription) => {
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

export default ActivationCodesUploadErrorDescription
