import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useRef, useState } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import Icon from 'components/layout/Icon'

import { ActivationCodeCsvForm } from './ActivationCodesCsvForm/ActivationCodesCsvForm'

export const ACTIVATION_CODES_UPLOAD_ID = 'ACTIVATION_CODES_UPLOAD_ID'

const getActivationCodesFromFileContent = fileContent => {
  const parsedFileContent = fileContent.split('\n')
  parsedFileContent.shift()

  return parsedFileContent
}

const ActivationCodesUploadDialog = ({ closeDialog }) => {
  const file = useRef({})

  const [isFileInputDisabled, setIsFileInputDisabled] = useState(false)
  const [activationCodes, setActivationCodes] = useState([])

  const submitThumbnail = useCallback(() => {
    setIsFileInputDisabled(true)
    const currentFile = file.current.files[0]
    const reader = new FileReader()
    if (currentFile == null) {
      return
    }
    reader.readAsText(currentFile)
    reader.onload = function () {
      const fileContent = reader.result
      setActivationCodes(getActivationCodesFromFileContent(fileContent))
      setIsFileInputDisabled(false)
    }
    reader.onerror = function () {
      // Errors should be handled in another ticket (7791)
      setIsFileInputDisabled(false)
    }
  }, [setIsFileInputDisabled])

  const clearActivationCodes = useCallback(() => setActivationCodes([]), [])

  return (
    <DialogBox
      extraClassNames="activation-codes-upload"
      hasCloseButton
      labelledBy={ACTIVATION_CODES_UPLOAD_ID}
      onDismiss={closeDialog}
    >
      <Fragment>
        <section className="activation-codes-upload-section">
          <h4
            className="activation-codes-upload-title"
            id={ACTIVATION_CODES_UPLOAD_ID}
          >
            {"Ajouter des codes d'activation"}
          </h4>
          <Icon
            alt="Ajouter des codes d'activation"
            aria-hidden
            className="activation-codes-upload-icon"
            role="img"
            svg="add-activation-code-light"
          />
        </section>
        {activationCodes.length == 0 && (
          <ActivationCodeCsvForm
            isFileInputDisabled={isFileInputDisabled}
            ref={file}
            submitThumbnail={submitThumbnail}
          />
        )}
        {activationCodes.length > 0 && (
          <Fragment>
            <div className="activation-codes-upload-information-message">
              <p>
                {`Vous êtes sur le point d'ajouter ${activationCodes.length} codes d'activation.`}
              </p>
              <p>
                {'La quantité disponible pour cette offre sera mise à jour dans vos stocks'}
              </p>
            </div>
            <div className="activation-codes-upload-confirmation-message">
              <p>
                {"Souhaitez-vous valider l'opération ?"}
              </p>
            </div>
            <span className="activation-codes-upload-confirmation-buttons">
              <button
                className="secondary-button activation-codes-upload-confirmation-button"
                onClick={clearActivationCodes}
                type="button"
              >
                {'Retour'}
              </button>
              <button
                className="primary-button activation-codes-upload-confirmation-button"
                type="button"
              >
                {'Valider'}
              </button>
            </span>
          </Fragment>
        )}
      </Fragment>
    </DialogBox>
  )
}

ActivationCodesUploadDialog.propTypes = {
  closeDialog: PropTypes.func.isRequired,
}

export default ActivationCodesUploadDialog
