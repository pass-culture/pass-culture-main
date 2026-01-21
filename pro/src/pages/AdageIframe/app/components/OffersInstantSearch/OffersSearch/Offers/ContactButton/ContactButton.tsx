import type React from 'react'
import { useRef, useState } from 'react'

import type { AdageFrontRoles } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullMailIcon from '@/icons/full-mail.svg'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

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

  const dialogTriggerRef = useRef<HTMLButtonElement>(null)

  const onConfirmDialog = () => {
    setIsDialogOpen(false)
  }

  const handleButtonClick = () => {
    if (!isPreview) {
      apiAdage.logContactModalButtonClick({
        iframeFrom: location.pathname,
        offerId,
        queryId,
        isFromNoResult: isInSuggestions,
        playlistId,
      })
    }
  }

  return (
    <DialogBuilder
      variant="drawer"
      trigger={
        <Button
          variant={ButtonVariant.PRIMARY}
          icon={fullMailIcon}
          onClick={handleButtonClick}
          label="Contacter le partenaire"
        />
      }
      open={isDialogOpen}
      onOpenChange={setIsDialogOpen}
    >
      <RequestFormDialog
        offerId={offerId}
        userEmail={userEmail}
        userRole={userRole}
        contactEmail={contactEmail ?? ''}
        contactPhone={contactPhone ?? ''}
        contactUrl={contactUrl ?? ''}
        contactForm={contactForm ?? ''}
        isPreview={isPreview}
        dialogTriggerRef={dialogTriggerRef}
        onConfirmDialog={onConfirmDialog}
      />
    </DialogBuilder>
  )
}
