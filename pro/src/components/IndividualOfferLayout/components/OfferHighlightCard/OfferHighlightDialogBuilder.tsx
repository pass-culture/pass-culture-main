import type { ReactNode } from 'react'

import type { ShortHighlightResponseModel } from '@/apiClient/v1'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { OfferHighlightForm } from '../OfferHighlightForm/OfferHighlightForm'

type OfferHighlightDialogBuilderProps = {
  isOpen: boolean
  onOpenChange: (param: boolean) => void
  offerId: number
  highlightRequests: Array<ShortHighlightResponseModel>
  children: ReactNode
}

export function OfferHighlightDialogBuilder({
  isOpen,
  onOpenChange,
  offerId,
  children,
  highlightRequests,
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
        onSuccess={() => onOpenChange(false)}
      />
    </DialogBuilder>
  )
}
