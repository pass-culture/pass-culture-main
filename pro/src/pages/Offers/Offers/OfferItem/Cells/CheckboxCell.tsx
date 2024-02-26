import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { isOfferDisabled } from 'core/Offers/utils'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

interface CheckboxCellProps {
  offerName: string
  isSelected: boolean
  offerId: number
  status: OfferStatus
  disabled: boolean
  isShowcase: boolean
  selectOffer: (offerId: number, selected: boolean, isTemplate: boolean) => void
}

export const CheckboxCell = ({
  offerName,
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
        className="select-offer-checkbox"
        label={offerName}
        exceptionnallyHideLabelDespiteA11y={true}
        disabled={disabled || isOfferDisabled(status)}
        onChange={handleOnChangeSelected}
      />
    </td>
  )
}
