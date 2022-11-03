import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useRef, useState } from 'react'

import DialogBox from 'new_components/DialogBox/DialogBox'

import { ReactComponent as ActivationCodeErrorIcon } from '../assets/add-activation-code-error.svg'
import { ReactComponent as AddActivationCodeIcon } from '../assets/add-activation-code-light.svg'

import ActivationCodesConfirmationForm from './ActivationCodesConfirmationForm/ActivationCodesConfirmationForm'
import { ActivationCodeCsvForm } from './ActivationCodesCsvForm/ActivationCodesCsvForm'
import { checkAndParseUploadedFile, fileReader } from './UploadedFileChecker'

export const ACTIVATION_CODES_UPLOAD_ID = 'ACTIVATION_CODES_UPLOAD_ID'

const ActivationCodesUploadDialog = ({
  activationCodes,
  activationCodesExpirationDatetime,
  bookingLimitDatetime,
  changeActivationCodesExpirationDatetime,
  closeDialog,
  setActivationCodes,
  today,
  validateActivationCodes,
}) => {
  const file = useRef({})

  const [errorMessage, setErrorMessage] = useState(null)
  const [fileName, setFileName] = useState('')
  const [isFileInputDisabled, setIsFileInputDisabled] = useState(false)

  const submitThumbnail = useCallback(async () => {
    setIsFileInputDisabled(true)
    const currentFile = file.current.files[0]
    if (currentFile == null) {
      setIsFileInputDisabled(false)
      return
    }

    const { errorMessage, activationCodes } = await checkAndParseUploadedFile({
      fileReader,
      currentFile,
    })

    setFileName(currentFile.name)
    file.current.value = '' // To detect input type=file “change” for the same file

    if (errorMessage) {
      setErrorMessage(errorMessage)
    } else {
      setErrorMessage(null)
      setActivationCodes(activationCodes)
    }

    setIsFileInputDisabled(false)
  }, [setActivationCodes, setIsFileInputDisabled])

  const clearActivationCodes = useCallback(() => {
    setActivationCodes([])
    setErrorMessage(null)
  }, [setActivationCodes])
  const submitActivationCodes = useCallback(() => {
    validateActivationCodes(activationCodes)
  }, [activationCodes, validateActivationCodes])

  return (
    <DialogBox
      extraClassNames="activation-codes-upload stocks-page"
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
            Ajouter des codes d’activation
          </h4>
          {errorMessage ? (
            <ActivationCodeErrorIcon
              alt="Erreur de validation des codes d’activation"
              aria-hidden
              className="activation-codes-upload-icon"
              data-testid="activation-codes-upload-error-icon-id"
            />
          ) : (
            <AddActivationCodeIcon
              alt="Ajouter des codes d’activation"
              aria-hidden
              className="activation-codes-upload-icon"
              data-testid="activation-codes-upload-icon-id"
            />
          )}
        </section>
        {activationCodes.length === 0 && (
          <ActivationCodeCsvForm
            errorMessage={errorMessage}
            fileName={fileName}
            isFileInputDisabled={isFileInputDisabled}
            ref={file}
            submitThumbnail={submitThumbnail}
          />
        )}
        {activationCodes.length > 0 && (
          <ActivationCodesConfirmationForm
            activationCodes={activationCodes}
            activationCodesExpirationDatetime={
              activationCodesExpirationDatetime
            }
            bookingLimitDatetime={bookingLimitDatetime}
            changeActivationCodesExpirationDatetime={
              changeActivationCodesExpirationDatetime
            }
            clearActivationCodes={clearActivationCodes}
            submitActivationCodes={submitActivationCodes}
            today={today}
          />
        )}
      </Fragment>
    </DialogBox>
  )
}

ActivationCodesUploadDialog.defaultProps = {
  activationCodesExpirationDatetime: null,
  bookingLimitDatetime: null,
}

ActivationCodesUploadDialog.propTypes = {
  activationCodes: PropTypes.arrayOf(PropTypes.string).isRequired,
  activationCodesExpirationDatetime: PropTypes.instanceOf(Date),
  bookingLimitDatetime: PropTypes.instanceOf(Date),
  changeActivationCodesExpirationDatetime: PropTypes.func.isRequired,
  closeDialog: PropTypes.func.isRequired,
  setActivationCodes: PropTypes.func.isRequired,
  today: PropTypes.instanceOf(Date).isRequired,
  validateActivationCodes: PropTypes.func.isRequired,
}

export default ActivationCodesUploadDialog
