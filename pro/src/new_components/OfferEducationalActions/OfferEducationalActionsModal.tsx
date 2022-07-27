import React, { useRef } from 'react'

import DialogBox from 'new_components/DialogBox'
import { Button, Title } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { ReactComponent as Trash } from './assets/trash.svg'
import styles from './OfferEducationalActionsModal.module.scss'

interface IOfferEducationalModalProps {
  onDismiss(): void
  onValidate(): void
}

const OfferEducationalModal = ({
  onDismiss,
  onValidate,
}: IOfferEducationalModalProps): JSX.Element => {
  const modalButtonRef = useRef<HTMLButtonElement>(null)

  return (
    <DialogBox
      extraClassNames={styles.modal}
      hasCloseButton
      initialFocusRef={modalButtonRef}
      labelledBy="Voulez-vous annuler la réservation ?"
      onDismiss={onDismiss}
    >
      <div className={styles['modal-icon-wrapper']}>
        <Trash />
      </div>
      <Title as="h2" className={styles['modal-header']} level={3}>
        Voulez-vous annuler la réservation ?
      </Title>
      <p className={styles['modal-paragraph']}>
        L’établissement scolaire concerné recevra un message lui indiquant
        l’annulation de sa réservation.
      </p>
      <div className={styles['modal-buttons']}>
        <Button
          className={styles['modal-button']}
          onClick={onDismiss}
          variant={ButtonVariant.SECONDARY}
        >
          Retour
        </Button>
        <Button
          className={styles['modal-button']}
          innerRef={modalButtonRef}
          onClick={onValidate}
          variant={ButtonVariant.PRIMARY}
        >
          Confirmer
        </Button>
      </div>
    </DialogBox>
  )
}

export default OfferEducationalModal
