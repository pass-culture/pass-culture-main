import classNames from 'classnames'

import styles from 'styles/components/Cells.module.scss'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

interface CheckboxCellProps {
  offerName: string
  isSelected: boolean
  disabled?: boolean
  selectOffer: () => void
  className?: string
}

export const CheckboxCell = ({
  offerName,
  isSelected,
  disabled,
  selectOffer,
  className,
}: CheckboxCellProps) => {
  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['checkbox-column'],
        className
      )}
    >
      <BaseCheckbox
        checked={isSelected}
        className="select-offer-checkbox"
        label={`Sélectionner l'offre "${offerName}"`}
        exceptionnallyHideLabelDespiteA11y={true}
        disabled={disabled}
        onChange={selectOffer}
      />
    </td>
  )
}
