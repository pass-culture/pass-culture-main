import React, { useState } from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { logClickOnOffer } from 'pages/AdageIframe/libs/initAlgoliaAnalytics'
import { Button } from 'ui-kit'

import RequestFormDialog from './RequestFormDialog'

export interface ContactButtonProps {
  className?: string
  contactEmail?: string
  contactPhone?: string | null
  offerId: number
  position: number
  queryId: string
  userEmail?: string | null
  userRole: AdageFrontRoles
  isInSuggestions?: boolean
  children?: React.ReactNode
}

const ContactButton = ({
  className,
  contactEmail,
  contactPhone,
  offerId,
  position,
  queryId,
  userEmail,
  userRole,
  isInSuggestions,
  children,
}: ContactButtonProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleButtonClick = () => {
    setIsModalOpen(true)

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    apiAdage.logContactModalButtonClick({
      iframeFrom: location.pathname,
      offerId,
      queryId: queryId,
      isFromNoResult: isInSuggestions,
    })
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    logClickOnOffer(offerId.toString(), position, queryId)
  }

  const closeModal = () => {
    setIsModalOpen(false)
  }

  return (
    <>
      <div className={`prebooking-button-container ${className}`}>
        <Button className="prebooking-button" onClick={handleButtonClick}>
          {children ?? 'Contacter'}
        </Button>
      </div>
      {isModalOpen && (
        <RequestFormDialog
          closeModal={closeModal}
          contactEmail={contactEmail}
          contactPhone={contactPhone}
          offerId={offerId}
          userEmail={userEmail}
          userRole={userRole}
        />
      )}
    </>
  )
}

export default ContactButton
