import React from 'react'

import { Offer } from 'core/Offers/types'
import fullStockIcon from 'icons/full-stock.svg'
import ListIconButton from 'ui-kit/ListIconButton/ListIconButton'

const EditStocksCell = ({
  editionStockLink,
  offer,
}: {
  editionStockLink: string
  offer: Offer
}) => {
  return (
    <ListIconButton url={editionStockLink} icon={fullStockIcon}>
      {offer.isEvent ? `Dates et capacités` : `Stocks`}
    </ListIconButton>
  )
}

export default EditStocksCell
