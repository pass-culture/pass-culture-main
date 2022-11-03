import React from 'react'

import { isOfferDisabled } from 'pages/Offers/domain/isOfferDisabled'

interface CheckboxCellProps {
  isSelected: boolean
  offerId: string
  status: string
  disabled: boolean
  isShowcase: boolean
  selectOffer: (offerId: string, selected: boolean, isTemplate: boolean) => void
}

const CheckboxCell = ({
  isSelected,
  offerId,
  status,
  disabled,
  isShowcase,
  selectOffer,
}: CheckboxCellProps) => {
  const handleOnChangeSelected = () => {
    selectOffer(offerId, !isSelected, !!isShowcase)
  }

  return (
    <td>
      <input
        checked={isSelected}
        data-testid={`select-offer-${offerId}`}
        disabled={disabled || isOfferDisabled(status)}
        id={`select-offer-${offerId}`}
        onChange={handleOnChangeSelected}
        type="checkbox"
      />
    </td>
  )
}

export default CheckboxCell
