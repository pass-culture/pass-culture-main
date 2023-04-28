import React from 'react'

import Dialog from 'components/Dialog/Dialog'
import { ReactComponent as MailOutlineIcon } from 'icons/ico-mail-outline.svg'
import { Button } from 'ui-kit'

import styles from './ContactDialog.module.scss'

interface IContactDialogProps {
  closeModal: () => void
  contactEmail?: string
  contactPhone?: string | null
}

const ContactDialog = ({
  closeModal,
  contactEmail,
  contactPhone,
}: IContactDialogProps): JSX.Element => {
  return (
    <Dialog
      onCancel={closeModal}
      title={'Contacter le partenaire culturel'}
      extraClassNames={styles['contact-modal-dialog']}
      icon={MailOutlineIcon}
    >
      <p className={styles['contact-modal-text']}>
        Afin de personnaliser cette offre, nous vous invitons à entrer en
        contact avec votre partenaire culturel :
      </p>
      <ul className={styles['contact-modal-list']}>
        <li>
          <a
            className={styles['contact-modal-list-item-link']}
            href={`mailto:${contactEmail}`}
          >
            {contactEmail}
          </a>
        </li>
        <li>{contactPhone}</li>
      </ul>
      <Button onClick={closeModal} className={styles['contact-modal-button']}>
        Fermer
      </Button>
    </Dialog>
  )
}

export default ContactDialog
