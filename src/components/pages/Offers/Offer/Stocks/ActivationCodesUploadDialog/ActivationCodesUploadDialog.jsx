import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useRef, useState } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import Icon from 'components/layout/Icon'

import ActivationCodesConfirmationForm from './ActivationCodesConfirmationForm/ActivationCodesConfirmationForm'
import { ActivationCodeCsvForm } from './ActivationCodesCsvForm/ActivationCodesCsvForm'

export const ACTIVATION_CODES_UPLOAD_ID = 'ACTIVATION_CODES_UPLOAD_ID'

const getActivationCodesFromFileContent = fileContent => {
  const parsedFileContent = fileContent.split('\n')
  parsedFileContent.shift()

  return parsedFileContent
}

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
            activationCodesExpirationDatetime={activationCodesExpirationDatetime}
            bookingLimitDatetime={bookingLimitDatetime}
            changeActivationCodesExpirationDatetime={changeActivationCodesExpirationDatetime}
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
