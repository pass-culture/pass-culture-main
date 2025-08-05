import { Dialog } from 'components/Dialog/Dialog'
import strokeCodeIcon from 'icons/stroke-code.svg'
import React, { useCallback, useState } from 'react'

import {
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
  activationCodeButtonRef: React.RefObject<HTMLButtonElement>
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
  const [errorMessage, setErrorMessage] = useState('')
  const [unsavedActivationCodes, setUnsavedActivationCodes] =
    useState<string[]>()
  const [isFileInputDisabled, setIsFileInputDisabled] = useState(false)
  const hasNoActivationCodes =
    unsavedActivationCodes === undefined || unsavedActivationCodes.length === 0

  const submitFile = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      setIsFileInputDisabled(true)

      const currentFile =
        e.currentTarget.files !== null ? e.currentTarget.files[0] : null
      if (currentFile === null) {
        setIsFileInputDisabled(false)
        return
      }

      const { errorMessage, activationCodes } = await checkAndParseUploadedFile(
        {
          fileReader,
          currentFile,
        }
      )

      if (errorMessage) {
        setErrorMessage(errorMessage)
      } else {
        if (!activationCodes) {
          setErrorMessage(
            "Aucune code d'activation n’est présent dans le fichier fourni"
          )
          return
        }
        setErrorMessage('')

        setUnsavedActivationCodes(activationCodes)
      }

      setIsFileInputDisabled(false)
    },
    [setUnsavedActivationCodes, setIsFileInputDisabled, setErrorMessage]
  )

  const dismissModal = useCallback(() => {
    onCancel()
  }, [onCancel])

  return (
    <Dialog
      onCancel={dismissModal}
      title="Ajouter des codes d’activation"
      icon={strokeCodeIcon}
      extraClassNames={styles['activation-codes-upload']}
      open={isDialogOpen}
      refToFocusOnClose={activationCodeButtonRef}
    >
      {hasNoActivationCodes && (
        <AddActivationCodeForm
          submitFile={submitFile}
          errorMessage={errorMessage}
          isFileInputDisabled={isFileInputDisabled}
        />
      )}

      {!hasNoActivationCodes && (
        <AddActivationCodeConfirmationForm
          unsavedActivationCodes={unsavedActivationCodes}
          clearActivationCodes={onCancel}
          submitActivationCodes={(expirationDate: string | undefined) =>
            onSubmit(unsavedActivationCodes, expirationDate)
          }
          today={today}
          minExpirationDate={minExpirationDate}
          departmentCode={departmentCode}
        />
      )}
    </Dialog>
  )
}
