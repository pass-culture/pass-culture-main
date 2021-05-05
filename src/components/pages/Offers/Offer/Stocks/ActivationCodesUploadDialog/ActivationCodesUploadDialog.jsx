import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useRef, useState } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import Icon from 'components/layout/Icon'

import { ActivationCodeCsvForm } from './ActivationCodesCsvForm/ActivationCodesCsvForm'
import ActivationCodesConfirmationForm from './ActivationCodesConfirmationForm/ActivationCodesConfirmationForm'

export const ACTIVATION_CODES_UPLOAD_ID = 'ACTIVATION_CODES_UPLOAD_ID'

const getActivationCodesFromFileContent = fileContent => {
  const parsedFileContent = fileContent.split('\n')
  parsedFileContent.shift()

  return parsedFileContent
}

const ActivationCodesUploadDialog = ({
  activationCodes,
  closeDialog,
  validateActivationCodes,
  setActivationCodes,
  setActivationCodesExpirationDatetime,
}) => {
  const file = useRef({})

  const [isFileInputDisabled, setIsFileInputDisabled] = useState(false)

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
  }, [setActivationCodes, setIsFileInputDisabled])

  const clearActivationCodes = useCallback(() => setActivationCodes([]), [setActivationCodes])
  const submitActivationCodes = useCallback(() => {
    validateActivationCodes(activationCodes)
  }, [activationCodes, validateActivationCodes])

  return (
    <DialogBox
      extraClassNames="activation-codes-upload"
      hasCloseButton
      labelledBy={ACTIVATION_CODES_UPLOAD_ID}
      onDismiss={closeDialog}
    >
      <Fragment>
        <section className="activation-codes-upload-section">
          <h4 className="activation-codes-upload-title" id={ACTIVATION_CODES_UPLOAD_ID}>
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
          <ActivationCodesConfirmationForm
            activationCodes={activationCodes}
            clearActivationCodes={clearActivationCodes}
            setActivationCodesExpirationDatetime={setActivationCodesExpirationDatetime}
            submitActivationCodes={submitActivationCodes}
          />
        )}
      </Fragment>
    </DialogBox>
  )
}

ActivationCodesUploadDialog.propTypes = {
  activationCodes: PropTypes.arrayOf(PropTypes.string).isRequired,
  closeDialog: PropTypes.func.isRequired,
  setActivationCodes: PropTypes.func.isRequired,
  setActivationCodesExpirationDatetime: PropTypes.func.isRequired,
  validateActivationCodes: PropTypes.func.isRequired,
}

export default ActivationCodesUploadDialog
