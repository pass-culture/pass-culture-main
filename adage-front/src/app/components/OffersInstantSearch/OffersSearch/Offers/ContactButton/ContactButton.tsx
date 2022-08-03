import { useMatomo } from '@datapunt/matomo-tracker-react'
import React, { useState } from 'react'

import { Button, ModalLayout } from 'app/ui-kit'
import { ReactComponent as MailIcon } from 'assets/mail.svg'

import './ContactButton.scss'

const ContactButton = ({
  className,
  contactEmail,
  contactPhone,
}: {
  className?: string
  contactEmail?: string
  contactPhone?: string
}): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { trackEvent } = useMatomo()

  const handleButtonClick = () => {
    trackEvent({
      category: 'button-click',
      action: 'modal-opening',
      name: 'ContactButtonClick',
    })
    setIsModalOpen(true)
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
