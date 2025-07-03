import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { CollectiveStatusLabel } from 'components/CollectiveStatusLabel/CollectiveStatusLabel'

interface CollectiveOfferStatusCellProps {
  rowId: string
  offer: CollectiveOfferResponseModel
  className?: string
}

export const CollectiveOfferStatusCell = ({
  offer,
}: CollectiveOfferStatusCellProps) => (
  <div>
    <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
  </div>
)
