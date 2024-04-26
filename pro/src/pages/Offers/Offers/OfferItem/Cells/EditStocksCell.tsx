import React from 'react'

import { ListOffersOfferResponseModel } from 'apiClient/v1'
import fullStockIcon from 'icons/full-stock.svg'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'

interface EditStocksCellProps {
  editionStockLink: string
  offer: ListOffersOfferResponseModel
}

export const EditStocksCell = ({
  editionStockLink,
  offer,
}: EditStocksCellProps) => {
  return (
    <ListIconButton url={editionStockLink} icon={fullStockIcon}>
      {offer.isEvent ? `Dates et capacités` : `Stocks`}
    </ListIconButton>
  )
}
