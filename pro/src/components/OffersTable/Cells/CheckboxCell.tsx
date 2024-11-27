import classNames from 'classnames'

import styles from 'styles/components/Cells.module.scss'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'


interface CheckboxCellProps {
  offerName: string
  isSelected: boolean
  disabled?: boolean
  selectOffer: () => void
  headers?: string
}

export const CheckboxCell = ({
  offerName,
  isSelected,
  disabled,
  selectOffer,
  headers,
}: CheckboxCellProps) => {
  return (
    <td
      className={classNames(
        styles['offers-table-cell'],
        styles['checkbox-column']
      )}
      headers={headers}
    >
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
