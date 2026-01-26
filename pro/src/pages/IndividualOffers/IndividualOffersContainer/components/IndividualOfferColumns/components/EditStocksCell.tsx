import type { ListOffersOfferResponseModel } from '@/apiClient/v1'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullStockIcon from '@/icons/full-stock.svg'
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
    <DropdownItem>
      <Button
        as="a"
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        to={editionStockLink}
        icon={fullStockIcon}
        label={offer.isEvent ? `Dates et capacités` : `Stocks`}
      />
    </DropdownItem>
  )
}
