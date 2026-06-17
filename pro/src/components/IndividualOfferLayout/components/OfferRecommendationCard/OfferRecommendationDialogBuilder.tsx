import type { ReactNode } from 'react'

import type { ProAdviceModel } from '@/apiClient/v1/new'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { OfferRecommendationForm } from './OfferRecommendationForm'

type OfferRecommendationDialogBuilderProps = {
  isOpen: boolean
  onOpenChange: (param: boolean) => void
  offerId: number
  proAdvice: ProAdviceModel | null
  children: ReactNode
  onSubmit?: () => void
  submitLabel?: string
}

export function OfferRecommendationDialogBuilder({
  isOpen,
  onOpenChange,
  offerId,
  children,
  proAdvice,
  onSubmit,
  submitLabel,
}: Readonly<OfferRecommendationDialogBuilderProps>) {
  return (
    <DialogBuilder
      open={isOpen}
      onOpenChange={onOpenChange}
      title="Ajouter votre recommandation"
      variant="drawer"
      trigger={children}
    >
      <OfferRecommendationForm
        offerId={offerId}
        proAdvice={proAdvice}
        onSuccess={() => {
          onOpenChange(false)
          onSubmit?.()
        }}
        submitLabel={submitLabel}
      />
    </DialogBuilder>
  )
}
