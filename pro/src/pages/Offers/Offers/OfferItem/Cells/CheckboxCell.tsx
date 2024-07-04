import { CollectiveOfferStatus, OfferStatus } from 'apiClient/v1'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

interface CheckboxCellProps {
  offerName: string
  isSelected: boolean
  status: OfferStatus | CollectiveOfferStatus
  disabled: boolean
  selectOffer: () => void
}

export const CheckboxCell = ({
  offerName,
  isSelected,
  status,
  disabled,
  selectOffer,
}: CheckboxCellProps) => {
  return (
    <td>
      <BaseCheckbox
        checked={isSelected}
        className="select-offer-checkbox"
        label={offerName}
        exceptionnallyHideLabelDespiteA11y={true}
        disabled={disabled || isOfferDisabled(status)}
        onChange={selectOffer}
      />
    </td>
  )
}
