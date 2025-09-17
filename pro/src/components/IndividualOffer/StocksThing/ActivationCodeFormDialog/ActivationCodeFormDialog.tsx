import type React from 'react'
import { useState } from 'react'

import { Dialog } from '@/components/Dialog/Dialog'
import strokeCodeIcon from '@/icons/stroke-code.svg'

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
  const [unsavedActivationCodes, setUnsavedActivationCodes] = useState<
    string[]
  >([])
  const [isFileInputDisabled, setIsFileInputDisabled] = useState(false)

  const loadCsvFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsFileInputDisabled(true)

    const currentFile =
      e.currentTarget.files !== null ? e.currentTarget.files[0] : null
    if (currentFile === null) {
      setIsFileInputDisabled(false)
      return
    }

    const { errorMessage, activationCodes } = await checkAndParseUploadedFile({
      fileReader,
      currentFile,
    })

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
  }

  const setExpirationDate = (expirationDate: string | undefined) => {
    onSubmit(unsavedActivationCodes, expirationDate)

    setUnsavedActivationCodes([])
  }

  return (
    <Dialog
      onCancel={onCancel}
      title="Ajouter des codes d’activation"
      icon={strokeCodeIcon}
      extraClassNames={styles['activation-codes-upload']}
      open={isDialogOpen}
      refToFocusOnClose={activationCodeButtonRef}
    >
      {unsavedActivationCodes.length === 0 ? (
        <AddActivationCodeForm
          submitFile={loadCsvFile}
          errorMessage={errorMessage}
          isFileInputDisabled={isFileInputDisabled}
        />
      ) : (
        <AddActivationCodeConfirmationForm
          unsavedActivationCodes={unsavedActivationCodes}
          clearActivationCodes={onCancel}
          submitActivationCodes={setExpirationDate}
          today={today}
          minExpirationDate={minExpirationDate}
          departmentCode={departmentCode}
        />
      )}
    </Dialog>
  )
}
