import React, { useState } from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { Button } from 'ui-kit/Button/Button'

import { RequestFormDialog } from './RequestFormDialog/RequestFormDialog'

export interface ContactButtonProps {
  className?: string
  contactEmail?: string | null
  contactPhone?: string | null
  contactForm?: string | null
  contactUrl?: string | null
  offerId: number
  queryId: string
  userEmail?: string | null
  userRole?: AdageFrontRoles
  isInSuggestions?: boolean
  children?: React.ReactNode
  isPreview?: boolean
}

export const ContactButton = ({
  className,
  contactEmail,
  contactPhone,
  contactForm,
  contactUrl,
  offerId,
  queryId,
  userEmail,
  userRole,
  isInSuggestions,
  children,
  isPreview = false,
}: ContactButtonProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleButtonClick = () => {
    setIsModalOpen(true)

    if (!isPreview) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      apiAdage.logContactModalButtonClick({
        iframeFrom: location.pathname,
        offerId,
        queryId: queryId,
        isFromNoResult: isInSuggestions,
      })
    }
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
          offerId={offerId}
          userEmail={userEmail}
          userRole={userRole}
          contactEmail={contactEmail ?? ''}
          contactPhone={contactPhone ?? ''}
          contactUrl={contactUrl ?? ''}
          contactForm={contactForm ?? ''}
          isPreview={isPreview}
        />
      )}
    </>
  )
}
