import React, { useState } from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import useActiveFeature from 'hooks/useActiveFeature'
import { logClickOnOffer } from 'pages/AdageIframe/libs/initAlgoliaAnalytics'
import { Button } from 'ui-kit'
import { removeParamsFromUrl } from 'utils/removeParamsFromUrl'

import ContactDialog from './ContactDialog'
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
}: ContactButtonProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleButtonClick = () => {
    setIsModalOpen(true)
    apiAdage.logContactModalButtonClick({
      iframeFrom: removeParamsFromUrl(location.pathname),
      offerId,
    })
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
          offerId={offerId}
          userEmail={userEmail}
          userRole={userRole}
        />
      )}
    </>
  )
}

export default ContactButton
