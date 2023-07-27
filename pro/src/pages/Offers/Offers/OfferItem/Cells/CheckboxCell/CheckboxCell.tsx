import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { isOfferDisabled } from 'core/Offers/utils'
import { BaseCheckbox } from 'ui-kit/form/shared'

interface CheckboxCellProps {
  isSelected: boolean
  offerId: number
  status: OfferStatus
  disabled: boolean
  isShowcase: boolean
  selectOffer: (offerId: number, selected: boolean, isTemplate: boolean) => void
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
      <BaseCheckbox
        checked={isSelected}
        data-testid={`select-offer-${offerId}`}
        disabled={disabled || isOfferDisabled(status)}
        id={`select-offer-${offerId}`}
        onChange={handleOnChangeSelected}
        label=""
      />
    </td>
  )
}

export default CheckboxCell
