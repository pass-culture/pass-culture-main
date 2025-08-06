import { ListOffersOfferResponseModel } from '@/apiClient//v1'
import fullStockIcon from '@/icons/full-stock.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { DropdownItem } from '@/ui-kit/DropdownMenuWrapper/DropdownItem'

interface EditStocksCellProps {
  editionStockLink: string
  offer: ListOffersOfferResponseModel
}

export const EditStocksCell = ({
  editionStockLink,
  offer,
}: EditStocksCellProps) => {
  return (
    <DropdownItem asChild>
      <ButtonLink to={editionStockLink} icon={fullStockIcon}>
        {offer.isEvent ? `Dates et capacités` : `Stocks`}
      </ButtonLink>
    </DropdownItem>
  )
}
