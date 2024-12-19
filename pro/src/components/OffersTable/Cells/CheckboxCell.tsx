import classNames from 'classnames'

import styles from 'styles/components/Cells.module.scss'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

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
