import { useState } from 'react'

import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import { Checkbox } from 'design-system/Checkbox/Checkbox'

import styles from './DuplicateOfferDialog.module.scss'

export const DuplicateOfferDialog = ({
  onCancel,
  onConfirm,
  isDialogOpen,
  refToFocusOnClose,
}: {
  onCancel: () => void
  onConfirm: (shouldNotDisplayModalAgain: boolean) => void
  isDialogOpen: boolean
  refToFocusOnClose?: React.RefObject<HTMLButtonElement>
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
      open={isDialogOpen}
      refToFocusOnClose={refToFocusOnClose}
    >
      <p className={styles['duplicate-offer-dialog-text']}>
        Les informations que vous avez renseignées dans l’offre vitrine seront
        copiées. Vous pourrez modifier les informations de l’offre. Il vous
        restera alors à sélectionner l’établissement scolaire qui a fait une
        demande et à renseigner les informations de dates et prix.
      </p>
      <Checkbox
        label="Je ne souhaite plus voir cette information"
        checked={isCheckboxChecked}
        onChange={() => setIsCheckboxChecked(!isCheckboxChecked)}
      />
    </ConfirmDialog>
  )
}
