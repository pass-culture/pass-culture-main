import { useState } from 'react'

import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

import styles from './DuplicateOfferDialog.module.scss'

export const DuplicateOfferDialog = ({
  onCancel,
  onConfirm,
}: {
  onCancel: () => void
  onConfirm: (shouldNotDisplayModalAgain: boolean) => void
}) => {
  const [isCheckboxChecked, setIsCheckboxChecked] = useState(false)

  return (
    <ConfirmDialog
      onCancel={onCancel}
      onConfirm={() => onConfirm(isCheckboxChecked)}
      title="Créer une offre réservable pour un établissement scolaire"
      confirmText="Créer une offre réservable"
      cancelText="Annuler"
      hideIcon
    >
      <p className={styles['duplicate-offer-dialog-text']}>
        Les informations que vous avez renseignées dans l’offre vitrine seront
        copiées. Vous pourrez modifier les informations de l’offre. Il vous
        restera alors à sélectionner l’établissement scolaire qui a fait une
        demande et à renseigner les informations de dates et prix.
      </p>
      <BaseCheckbox
        label="Je ne souhaite plus voir cette information"
        checked={isCheckboxChecked}
        onChange={() => setIsCheckboxChecked(!isCheckboxChecked)}
      />
    </ConfirmDialog>
  )
}
