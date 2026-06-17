import type { ReactNode } from 'react'

import type { ShortHighlightResponseModel } from '@/apiClient/v1/new'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { OfferHighlightForm } from '../OfferHighlightForm/OfferHighlightForm'

type OfferHighlightDialogBuilderProps = {
  isOpen: boolean
  onOpenChange: (param: boolean) => void
  offerId: number
  highlightRequests: Array<ShortHighlightResponseModel>
  children: ReactNode
  onSubmit?: () => void
  submitLabel?: string
}

export function OfferHighlightDialogBuilder({
  isOpen,
  onOpenChange,
  offerId,
  children,
  highlightRequests,
  onSubmit,
  submitLabel,
}: Readonly<OfferHighlightDialogBuilderProps>) {
  return (
    <DialogBuilder
      open={isOpen}
      onOpenChange={onOpenChange}
      title="Choisir un temps fort"
      variant="drawer"
      trigger={children}
    >
      <OfferHighlightForm
        offerId={offerId}
        highlightRequests={highlightRequests}
        onSuccess={() => {
          onOpenChange(false)
          onSubmit?.()
        }}
        submitLabel={submitLabel}
      />
    </DialogBuilder>
  )
}
