import React, { useState } from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { logClickOnOffer } from 'pages/AdageIframe/libs/initAlgoliaAnalytics'
import { Button } from 'ui-kit/Button/Button'

import { NewRequestFormDialog } from './RequestFormDialog/NewRequestFormDialog'
import { RequestFormDialog } from './RequestFormDialog/RequestFormDialog'

export interface ContactButtonProps {
  className?: string
  contactEmail?: string | null
  contactPhone?: string | null
  contactForm?: string | null
  contactUrl?: string | null
  offerId: number
  position: number
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
  position,
  queryId,
  userEmail,
  userRole,
  isInSuggestions,
  children,
  isPreview = false,
}: ContactButtonProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const isCustomContactActive = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_CUSTOM_CONTACT'
  )

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
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      logClickOnOffer(offerId.toString(), position, queryId)
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
      {isModalOpen &&
        (isCustomContactActive ? (
          <NewRequestFormDialog
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
        ) : (
          <RequestFormDialog
            closeModal={closeModal}
            contactEmail={contactEmail}
            contactPhone={contactPhone}
            offerId={offerId}
            userEmail={userEmail}
            userRole={userRole}
            isPreview={isPreview}
          />
        ))}
    </>
  )
}
