import React, { useState } from 'react'

import { apiAdage } from 'apiClient/api'
import { logClickOnOffer } from 'pages/AdageIframe/libs/initAlgoliaAnalytics'
import { Button } from 'ui-kit'

import ContactDialog from './ContactDialog'

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
        <ContactDialog
          closeModal={closeModal}
          contactEmail={contactEmail}
          contactPhone={contactPhone}
        />
      )}
    </>
  )
}

export default ContactButton
