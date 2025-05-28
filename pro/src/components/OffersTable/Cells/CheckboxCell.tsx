import classNames from 'classnames'

import { Checkbox } from 'design-system/Checkbox/Checkbox'
import styles from 'styles/components/Cells.module.scss'

import { CELLS_DEFINITIONS } from '../utils/cellDefinitions'

interface CheckboxCellProps {
  offerName: string
  isSelected: boolean
  disabled?: boolean
  selectOffer: () => void
  rowId: string
  className?: string
}

export const CheckboxCell = ({
  offerName,
  isSelected,
  disabled,
  selectOffer,
  rowId,
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
      headers={`${rowId} ${CELLS_DEFINITIONS.CHECKBOX.id}`}
    >
      <Checkbox
        checked={isSelected}
        label={offerName}
        disabled={disabled}
        onChange={selectOffer}
        className={styles['label']}
      />
    </td>
  )
}
