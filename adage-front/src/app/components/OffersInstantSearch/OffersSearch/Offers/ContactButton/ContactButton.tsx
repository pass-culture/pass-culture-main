import React, { useState } from 'react'

import { api } from 'apiClient/api'
import { Button, ModalLayout } from 'app/ui-kit'
import { ReactComponent as MailIcon } from 'assets/mail.svg'
import './ContactButton.scss'
import { logClickOnOffer } from 'libs/initAlgoliaAnalytics'

const ContactButton = ({
  className,
  contactEmail,
  contactPhone,
  offerId,
  position,
  queryId,
}: {
  className?: string
  contactEmail?: string
  contactPhone?: string
  offerId: number
  position: number
  queryId: string
}): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleButtonClick = () => {
    setIsModalOpen(true)
    api.logContactModalButtonClick({ offerId })
    logClickOnOffer(offerId.toString(), position, queryId)
  }

  const closeModal = () => {
    setIsModalOpen(false)
  }

  return (
    <>
      <div className={`prebooking-button-container ${className}`}>
        <Button
          className="prebooking-button"
          label="Contacter"
          onClick={handleButtonClick}
          type="button"
        />
      </div>
      <ModalLayout Icon={MailIcon} closeModal={closeModal} isOpen={isModalOpen}>
        <p className="contact-modal-text">
          Afin de personnaliser cette offre, nous vous invitons à entrer en
          contact avec votre partenaire culturel :
        </p>
        <ul className="contact-modal-list">
          <li>
            <a
              className="contact-modal-list-item-link"
              href={`mailto:${contactEmail}`}
            >
              {contactEmail}
            </a>
          </li>
          <li>{contactPhone}</li>
        </ul>
      </ModalLayout>
    </>
  )
}

export default ContactButton
