import { GET_OFFER_PRO_ADVICE_QUERY_KEY } from 'commons/config/swrQueryKeys'
import useSWR from 'swr'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import type { ProAdviceModel } from '@/apiClient/v1'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'

import { api } from 'apiClient/api'
import {
  OFFER_RECOMMENDATION_FORM_ID,
  OfferRecommendationForm,
} from './OfferRecommendationForm'

type OfferRecommendationModalProps = {
  isOpen: boolean
  onOpenChange: (param: boolean) => void
  offerId: number
  proAdvice: ProAdviceModel | null
  loadAdviceFromOffer?: boolean
  onSubmit?: () => void
  submitLabel?: string
}

export function OfferRecommendationModal({
  isOpen,
  onOpenChange,
  offerId,
  proAdvice,
  onSubmit,
  submitLabel,
  loadAdviceFromOffer = false,
}: Readonly<OfferRecommendationModalProps>) {
  const { data: proAdviceResponse, isLoading } = useSWR(
    loadAdviceFromOffer && isOpen
      ? [GET_OFFER_PRO_ADVICE_QUERY_KEY, offerId]
      : null,
    () => api.getOfferProAdvice({ path: { offer_id: offerId } })
  )

  const advice = proAdvice || proAdviceResponse?.proAdvice

  return (
    <DetailedModal
      isOpen={isOpen}
      onClose={() => onOpenChange(false)}
      title="Ajouter votre recommandation"
      primaryAction={
        <Button
          type="submit"
          form={OFFER_RECOMMENDATION_FORM_ID}
          label={submitLabel ?? 'Enregistrer la recommandation'}
        />
      }
      secondaryAction={
        <Button
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          onClick={() => onOpenChange(false)}
          label="Fermer"
        />
      }
    >
      {isOpen &&
        (loadAdviceFromOffer && isLoading ? (
          <Spinner />
        ) : (
          <OfferRecommendationForm
            offerId={offerId}
            proAdvice={advice ?? null}
            onSuccess={() => {
              onOpenChange(false)
              onSubmit?.()
            }}
          />
        ))}
    </DetailedModal>
  )
}
