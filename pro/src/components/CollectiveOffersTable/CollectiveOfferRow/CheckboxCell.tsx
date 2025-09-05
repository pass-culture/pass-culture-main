import classNames from 'classnames'

import { Checkbox } from '@/design-system/Checkbox/Checkbox'

import { getCellsDefinition } from '../utils/cellDefinitions'
import styles from './Cells.module.scss'

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
      className={classNames(
        styles['offers-table-cell'],
        styles['checkbox-column'],
        className
      )}
      headers={`${rowId} ${getCellsDefinition().CHECKBOX.id}`}
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
