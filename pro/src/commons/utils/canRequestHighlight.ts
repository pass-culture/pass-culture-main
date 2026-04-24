import {
  type GetIndividualOfferResponseModel,
  OfferStatus,
} from '@/apiClient/v1'

type canRequestHighlightProps = {
  offer: GetIndividualOfferResponseModel
}
export const canRequestHighlight = ({ offer }: canRequestHighlightProps) => {
  return (
    offer.isEvent &&
    ![OfferStatus.PENDING, OfferStatus.REJECTED, OfferStatus.DRAFT].includes(
      offer.status
    )
  )
}
