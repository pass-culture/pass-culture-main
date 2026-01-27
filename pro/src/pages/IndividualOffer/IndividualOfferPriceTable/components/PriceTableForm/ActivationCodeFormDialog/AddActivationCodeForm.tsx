import type React from 'react'

import { Button } from '@/design-system/Button/Button'
import fullDownloadIcon from '@/icons/full-download.svg'
import { BaseFileInput } from '@/ui-kit/form/shared/BaseFileInput/BaseFileInput'

import styles from './ActivationCodeFormDialog.module.scss'
import { ActivationCodesUploadInformationDescription } from './ActivationCodesUploadInformationDescription'

interface AddActivationCodeFormProps {
  submitFile: (e: React.ChangeEvent<HTMLInputElement>) => void
  isFileInputDisabled: boolean
  errorMessage: string
}

export const AddActivationCodeForm = ({
  submitFile,
  isFileInputDisabled,
  errorMessage,
}: AddActivationCodeFormProps) => {
  return (
    <>
      {errorMessage ? (
        <div className={styles['activation-codes-errors']}>
          <p>Une erreur s’est produite lors de l’import de votre fichier.</p>
          <p>{errorMessage}</p>
          <p>Veuillez réessayer.</p>
        </div>
      ) : (
        <ActivationCodesUploadInformationDescription />
      )}
      <BaseFileInput
        label="Importer un fichier .csv depuis l’ordinateur"
        fileTypes={['.csv']}
        isValid={!errorMessage}
        isDisabled={isFileInputDisabled}
        onChange={submitFile}
      />

      <div className={styles['activation-codes-upload-button-caption']}>
        <p>Format supporté : CSV</p>
        <p>Le poids du fichier ne doit pas dépasser 1 Mo</p>
      </div>
      <div className={styles['activation-codes-upload-separator']} />
      <div className={styles['activation-codes-upload-template-section']}>
        <p className={styles['activation-codes-upload-gabarit']}>Gabarits</p>
        <Button
          as="a"
          isExternal
          to="/csvtemplates/CodesActivations-Gabarit.csv"
          // type="text/csv" // TODO: jclery-pass: Refactor <Button as="a"> polymorphic component to accept "string | undefined"
          opensInNewTab
          icon={fullDownloadIcon}
          label="Gabarit CSV(.csv, 50 ko)"
        />
      </div>
    </>
  )
}
