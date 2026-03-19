import type { ReactNode } from 'react'

import type { ProAdviceModel } from '@/apiClient/v1'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { OfferRecommendationForm } from './OfferRecommendationForm'

type OfferRecommendationDialogBuilderProps = {
  isOpen: boolean
  onOpenChange: (param: boolean) => void
  offerId: number
  proAdvice: ProAdviceModel | null
  children: ReactNode
}

export function OfferRecommendationDialogBuilder({
  isOpen,
  onOpenChange,
  offerId,
  children,
  proAdvice,
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
        onClose={() => onOpenChange(false)}
      />
    </DialogBuilder>
  )
}
