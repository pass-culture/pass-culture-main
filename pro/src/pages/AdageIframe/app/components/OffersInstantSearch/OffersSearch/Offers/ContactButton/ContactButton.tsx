import React, { useState } from 'react'

import { apiAdage } from 'apiClient/api'
import Dialog from 'components/Dialog/Dialog'
import { ReactComponent as MailOutlineIcon } from 'icons/ico-mail-outline.svg'
import { logClickOnOffer } from 'pages/AdageIframe/libs/initAlgoliaAnalytics'
import { Button } from 'ui-kit'

import styles from './ContactButton.module.scss'

export interface IContactButtonProps {
  className?: string
  contactEmail?: string
  contactPhone?: string | null
  offerId: number
  position: number
  queryId: string
}

const ContactButton = ({
  className,
  contactEmail,
  contactPhone,
  offerId,
  position,
  queryId,
}: IContactButtonProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleButtonClick = () => {
    setIsModalOpen(true)
    apiAdage.logContactModalButtonClick({ offerId })
    logClickOnOffer(offerId.toString(), position, queryId)
  }

  const closeModal = () => {
    setIsModalOpen(false)
  }

  return (
    <>
      <div className={`prebooking-button-container ${className}`}>
        <Button className="prebooking-button" onClick={handleButtonClick}>
          Contacter
        </Button>
      </div>
      {isModalOpen && (
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
          <Button
            onClick={closeModal}
            className={styles['contact-modal-button']}
          >
            Fermer
          </Button>
        </Dialog>
      )}
    </>
  )
}

export default ContactButton
