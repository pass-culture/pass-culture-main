import type { ShortHighlightResponseModel } from '@/apiClient/v1'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'

import {
  OFFER_HIGHLIGHT_FORM_ID,
  OfferHighlightForm,
} from '../OfferHighlightForm/OfferHighlightForm'

type OfferHighlightModalProps = {
  isOpen: boolean
  onOpenChange: (param: boolean) => void
  offerId: number
  highlightRequests: Array<ShortHighlightResponseModel>
  onSubmit?: () => void
  submitLabel?: string
}

export function OfferHighlightModal({
  isOpen,
  onOpenChange,
  offerId,
  highlightRequests,
  onSubmit,
  submitLabel,
}: Readonly<OfferHighlightModalProps>) {
  return (
    <DetailedModal
      isOpen={isOpen}
      onClose={() => onOpenChange(false)}
      title="Choisir un temps fort"
      primaryAction={
        <Button
          type="submit"
          form={OFFER_HIGHLIGHT_FORM_ID}
          label={submitLabel ?? 'Valider la sélection'}
        />
      }
      secondaryAction={
        <Button
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          onClick={() => onOpenChange(false)}
          label="Annuler"
        />
      }
      isFooterFixed
    >
      {isOpen && (
        <OfferHighlightForm
          offerId={offerId}
          highlightRequests={highlightRequests}
          onSuccess={() => {
            onOpenChange(false)
            onSubmit?.()
          }}
        />
      )}
    </DetailedModal>
  )
}
