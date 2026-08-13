import { useState } from 'react'

import type { AdageFrontRoles } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullMailIcon from '@/icons/full-mail.svg'

import { RequestFormDialog } from './RequestFormDialog/RequestFormDialog'

export interface ContactButtonProps {
  contactEmail?: string | null
  contactPhone?: string | null
  contactForm?: string | null
  contactUrl?: string | null
  offerId: number
  queryId: string
  userEmail?: string | null
  userRole?: AdageFrontRoles
  isInSuggestions?: boolean
  isPreview?: boolean
  playlistId?: number
}

export const ContactButton = ({
  contactEmail,
  contactPhone,
  contactForm,
  contactUrl,
  offerId,
  queryId,
  userEmail,
  userRole,
  isInSuggestions,
  isPreview = false,
  playlistId,
}: ContactButtonProps): JSX.Element => {
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const onConfirmDialog = () => {
    setIsDialogOpen(false)
  }

  const handleButtonClick = () => {
    if (!isPreview) {
      apiAdage.logContactModalButtonClick({
        body: {
          iframeFrom: location.pathname,
          offerId,
          queryId,
          isFromNoResult: isInSuggestions,
          playlistId,
        },
      })
    }
  }

  return (
    <>
      <Button
        variant={ButtonVariant.PRIMARY}
        icon={fullMailIcon}
        onClick={() => {
          handleButtonClick()
          setIsDialogOpen(true)
        }}
        label="Contacter le partenaire"
      />
      {isDialogOpen && (
        <RequestFormDialog
          offerId={offerId}
          userEmail={userEmail}
          userRole={userRole}
          contactEmail={contactEmail ?? ''}
          contactPhone={contactPhone ?? ''}
          contactUrl={contactUrl ?? ''}
          contactForm={contactForm ?? ''}
          isPreview={isPreview}
          isDialogOpen={isDialogOpen}
          onCloseDialog={() => setIsDialogOpen(false)}
          onConfirmDialog={onConfirmDialog}
        />
      )}
    </>
  )
}
