import React from 'react'

import Dialog from 'components/Dialog/Dialog'
import strokeMailIcon from 'icons/stroke-mail.svg'
import { Button } from 'ui-kit'

import styles from './ContactDialog.module.scss'

interface ContactDialogProps {
  closeModal: () => void
  contactEmail?: string
  contactPhone?: string | null
}

const ContactDialog = ({
  closeModal,
  contactEmail,
  contactPhone,
}: ContactDialogProps): JSX.Element => {
  return (
    <Dialog
      onCancel={closeModal}
      title="Contacter le partenaire culturel"
      extraClassNames={styles['contact-modal-dialog']}
      icon={strokeMailIcon}
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
