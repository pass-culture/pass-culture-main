import React, { useState } from 'react'

import { apiAdage } from 'apiClient/api'
import useActiveFeature from 'hooks/useActiveFeature'
import { logClickOnOffer } from 'pages/AdageIframe/libs/initAlgoliaAnalytics'
import { Button } from 'ui-kit'

import ContactDialog from './ContactDialog'
import RequestFormDialog from './RequestFormDialog'

export interface IContactButtonProps {
  className?: string
  contactEmail?: string
  contactPhone?: string | null
  venueName: string
  offererName: string
  offerId: number
  position: number
  queryId: string
}

const ContactButton = ({
  className,
  contactEmail,
  contactPhone,
  venueName,
  offererName,
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
  const isCollectiveRequestActive = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_REQUEST'
  )

  return (
    <>
      <div className={`prebooking-button-container ${className}`}>
        <Button className="prebooking-button" onClick={handleButtonClick}>
          Contacter
        </Button>
      </div>
      {isModalOpen && !isCollectiveRequestActive && (
        <ContactDialog
          closeModal={closeModal}
          contactEmail={contactEmail}
          contactPhone={contactPhone}
        />
      )}
      {isModalOpen && isCollectiveRequestActive && (
        <RequestFormDialog
          closeModal={closeModal}
          contactEmail={contactEmail}
          contactPhone={contactPhone}
          venueName={venueName}
          offererName={offererName}
        />
      )}
    </>
  )
}

export default ContactButton
