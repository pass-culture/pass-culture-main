import type React from 'react'
import { useEffect, useRef, useState } from 'react'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'

import {
  ActivationCodeFileErrorCode,
  checkAndParseUploadedFile,
  fileReader,
} from './ActivationCodeFileChecker'
import styles from './ActivationCodeFormDialog.module.scss'
import { AddActivationCodeConfirmationForm } from './AddActivationCodeConfirmationForm'
import { AddActivationCodeForm } from './AddActivationCodeForm'

interface ActivationCodeFormProps {
  onCancel: () => void
  onSubmit: (
    activationCodes: string[],
    expirationDate: string | undefined
  ) => void
  today: Date
  minExpirationDate: Date | null
  isDialogOpen: boolean
  activationCodeButtonRef: React.RefObject<HTMLButtonElement | null>
  departmentCode: string
}

export const ActivationCodeFormDialog = ({
  onCancel,
  onSubmit,
  today,
  minExpirationDate,
  isDialogOpen,
  activationCodeButtonRef,
  departmentCode,
}: ActivationCodeFormProps) => {
  const wasDialogOpen = useRef(isDialogOpen)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [errorTitle, setErrorTitle] = useState('')
  const [unsavedActivationCodes, setUnsavedActivationCodes] = useState<
    string[]
  >([])
  const [isFileInputDisabled, setIsFileInputDisabled] = useState(false)
  const [isFilePickerOpening, setIsFilePickerOpening] = useState(false)
  const [expirationDate, setExpirationDate] = useState<string | undefined>()

  const loadCsvFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsFileInputDisabled(true)
    setIsFilePickerOpening(false)

    const currentFile =
      e.currentTarget.files !== null ? e.currentTarget.files[0] : null
    if (currentFile === null) {
      setIsFileInputDisabled(false)
      return
    }

    const { errorCode, errorMessage, activationCodes } =
      await checkAndParseUploadedFile({
        fileReader,
        currentFile,
      })

    if (errorMessage) {
      if (errorCode === ActivationCodeFileErrorCode.INVALID_FORMAT) {
        setErrorTitle('Format invalide')
      } else if (errorCode === ActivationCodeFileErrorCode.FILE_TOO_LARGE) {
        setErrorTitle('Fichier trop lourd')
      } else {
        setErrorTitle('Import impossible')
      }
      setErrorMessage(errorMessage)
    } else {
      if (!activationCodes) {
        setErrorTitle('Import impossible')
        setErrorMessage(
          "Aucune code d'activation n’est présent dans le fichier fourni"
        )
        return
      }
      setErrorTitle('')
      setErrorMessage('')

      setUnsavedActivationCodes(activationCodes)
    }

    setIsFileInputDisabled(false)
  }

  const clearUnsavedActivationCodes = () => {
    setUnsavedActivationCodes([])
    setExpirationDate(undefined)
  }

  const handleModalClose = () => {
    if (isFilePickerOpening) {
      setIsFilePickerOpening(false)
      return
    }
    onCancel()
  }

  const submitActivationCodes = (expirationDate: string | undefined) => {
    if (!expirationDate) {
      return
    }

    onSubmit(unsavedActivationCodes, expirationDate)

    setUnsavedActivationCodes([])
    setExpirationDate(undefined)
  }

  const openFilePicker = () => {
    if (isFileInputDisabled) {
      return
    }

    setIsFilePickerOpening(true)
    fileInputRef.current?.click()
  }

  const isConfirmationStep = unsavedActivationCodes.length > 0

  useEffect(() => {
    if (wasDialogOpen.current && !isDialogOpen) {
      activationCodeButtonRef.current?.focus()
    }
    wasDialogOpen.current = isDialogOpen
  }, [activationCodeButtonRef, isDialogOpen])

  if (!isDialogOpen) {
    return null
  }

  return (
    <DetailedModal
      isOpen={isDialogOpen}
      onClose={handleModalClose}
      title={
        isConfirmationStep
          ? 'Ajouter des codes d’activation 2/2'
          : 'Ajouter des codes d’activation 1/2'
      }
      onGoBack={isConfirmationStep ? clearUnsavedActivationCodes : undefined}
      goBackButtonAriaLabel="Retour à l’étape d’import"
      description={
        !isConfirmationStep
          ? 'Pour les offres nécessitant une activation par code sur une plateforme extérieure, vous pouvez importer directement un fichier .csv. Le poids de ce fichier ne doit pas dépasser 1 Mo.'
          : `Vous êtes sur le point d’ajouter ${unsavedActivationCodes.length} codes d’activation. La quantité disponible pour cette offre sera mise à jour dans vos stocks.`
      }
      secondaryAction={
        isConfirmationStep ? (
          <Button
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            onClick={onCancel}
            label="Annuler"
          />
        ) : (
          <Button
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            onClick={onCancel}
            label="Fermer"
          />
        )
      }
      primaryAction={
        isConfirmationStep ? (
          <Button
            onClick={() => submitActivationCodes(expirationDate)}
            label="Ajouter les codes de validation"
            disabled={!expirationDate}
          />
        ) : (
          <Button
            onClick={openFilePicker}
            label="Importer un fichier .csv"
            disabled={isFileInputDisabled}
          />
        )
      }
      isFooterFixed
    >
      <div className={styles['activation-codes-upload']}>
        {!isConfirmationStep ? (
          <>
            <input
              ref={fileInputRef}
              accept=".csv"
              aria-invalid={!!errorMessage}
              aria-label="Importer un fichier .csv depuis l’ordinateur"
              className={styles['activation-codes-hidden-input']}
              type="file"
              disabled={isFileInputDisabled}
              onClick={() => setIsFilePickerOpening(true)}
              onChange={loadCsvFile}
            />
            <AddActivationCodeForm
              errorMessage={errorMessage}
              errorTitle={errorTitle}
            />
          </>
        ) : (
          <AddActivationCodeConfirmationForm
            onExpirationDateChange={setExpirationDate}
            today={today}
            minExpirationDate={minExpirationDate}
            departmentCode={departmentCode}
          />
        )}
      </div>
    </DetailedModal>
  )
}
