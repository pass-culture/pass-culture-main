import React from 'react'

import DialogBox from 'new_components/DialogBox'
import { Button, Title } from 'ui-kit'

import { ReactComponent as Trash } from './assets/trash.svg'
import styles from './OfferEducationalActionsModal.module.scss'

interface IOfferEducationalModalProps {
  onDismiss(): void
  onValidate(): void
  modalButtonRef: React.RefObject<HTMLButtonElement>
}

const OfferEducationalModal = ({
  onDismiss,
  onValidate,
  modalButtonRef,
}: IOfferEducationalModalProps): JSX.Element => (
  <DialogBox
    extraClassNames={styles['modal']}
    hasCloseButton
    initialFocusRef={modalButtonRef}
    labelledBy=""
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
      l’annulation de sa réservation.{' '}
    </p>
    <div className={styles['modal-buttons']}>
      <Button
        className={styles['modal-button']}
        onClick={onDismiss}
        variant={Button.variant.SECONDARY}
      >
        Annuller
      </Button>
      <Button
        className={styles['modal-button']}
        onClick={onValidate}
        ref={modalButtonRef}
        variant={Button.variant.PRIMARY}
      >
        Supprimer
      </Button>
    </div>
  </DialogBox>
)

export default OfferEducationalModal
