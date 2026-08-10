import { useState } from 'react'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'

import styles from './DuplicateOfferDialog.module.scss'

export const DuplicateOfferDialog = ({
  onCancel,
  onConfirm,
  isDialogOpen,
}: {
  onCancel: () => void
  onConfirm: (shouldNotDisplayModalAgain: boolean) => void
  isDialogOpen: boolean
}) => {
  const [isCheckboxChecked, setIsCheckboxChecked] = useState(false)

  return (
    <SimpleModal
      title="Créer une offre réservable pour un établissement scolaire"
      isOpen={isDialogOpen}
      onClose={onCancel}
      actionButtons={
        <>
          <Button
            onClick={onCancel}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Annuler"
          />
          <Button
            onClick={() => onConfirm(isCheckboxChecked)}
            label="Créer une offre réservable"
          />
        </>
      }
    >
      <p className={styles['duplicate-offer-dialog-text']}>
        Les informations que vous avez renseignées dans l'offre vitrine seront
        copiées. Vous pourrez modifier les informations de l'offre. Il vous
        restera alors à sélectionner l'établissement scolaire qui a fait une
        demande et à renseigner les informations de dates et prix.
      </p>
      <Checkbox
        label="Je ne souhaite plus voir cette information"
        checked={isCheckboxChecked}
        onChange={() => setIsCheckboxChecked(!isCheckboxChecked)}
      />
    </SimpleModal>
  )
}
