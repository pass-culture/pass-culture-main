import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

import styles from '../OfferItem.module.scss'

interface CheckboxCellProps {
  offerName: string
  isSelected: boolean
  disabled?: boolean
  selectOffer: () => void
}

export const CheckboxCell = ({
  offerName,
  isSelected,
  disabled,
  selectOffer,
}: CheckboxCellProps) => {
  return (
    <td className={styles['checkbox-column']}>
      <BaseCheckbox
        checked={isSelected}
        className="select-offer-checkbox"
        label={offerName}
        exceptionnallyHideLabelDespiteA11y={true}
        disabled={disabled}
        onChange={selectOffer}
      />
    </td>
  )
}
