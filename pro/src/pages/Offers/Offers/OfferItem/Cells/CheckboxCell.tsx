import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

interface CheckboxCellProps {
  offerName: string
  isSelected: boolean
  offerId: number
  status: OfferStatus
  disabled: boolean
  selectOffer: (offerId: number, selected: boolean) => void
}

export const CheckboxCell = ({
  offerName,
  isSelected,
  offerId,
  status,
  disabled,
  selectOffer,
}: CheckboxCellProps) => {
  const handleOnChangeSelected = () => {
    selectOffer(offerId, !isSelected)
  }

  return (
    <td>
      <BaseCheckbox
        checked={isSelected}
        className="select-offer-checkbox"
        label={offerName}
        exceptionnallyHideLabelDespiteA11y={true}
        disabled={disabled || isOfferDisabled(status)}
        onChange={handleOnChangeSelected}
      />
    </td>
  )
}
