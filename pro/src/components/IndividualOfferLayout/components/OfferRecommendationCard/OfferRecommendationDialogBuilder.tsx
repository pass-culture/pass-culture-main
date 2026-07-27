import { GET_OFFER_PRO_ADVICE_QUERY_KEY } from 'commons/config/swrQueryKeys'
import type { ReactNode } from 'react'
import useSWR from 'swr'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import type { ProAdviceModel } from '@/apiClient/v1'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { api } from 'apiClient/api'
import { OfferRecommendationForm } from './OfferRecommendationForm'

type OfferRecommendationDialogBuilderProps = {
  isOpen: boolean
  onOpenChange: (param: boolean) => void
  offerId: number
  proAdvice: ProAdviceModel | null
  loadAdviceFromOffer?: boolean
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
  loadAdviceFromOffer = false,
}: Readonly<OfferRecommendationDialogBuilderProps>) {
  const { data: proAdviceResponse, isLoading } = useSWR(
    loadAdviceFromOffer && isOpen
      ? [GET_OFFER_PRO_ADVICE_QUERY_KEY, offerId]
      : null,
    () => api.getOfferProAdvice({ path: { offer_id: offerId } })
  )

  const advice = proAdvice || proAdviceResponse?.proAdvice

  console.log('proAdviceResponse', proAdviceResponse?.proAdvice)
  return (
    <DialogBuilder
      open={isOpen}
      onOpenChange={onOpenChange}
      title="Ajouter votre recommandation"
      variant="drawer"
      trigger={children}
    >
      {loadAdviceFromOffer && isLoading ? (
        <Spinner />
      ) : (
        <OfferRecommendationForm
          offerId={offerId}
          proAdvice={advice ?? null}
          onSuccess={() => {
            onOpenChange(false)
            onSubmit?.()
          }}
          submitLabel={submitLabel}
        />
      )}
    </DialogBuilder>
  )
}
