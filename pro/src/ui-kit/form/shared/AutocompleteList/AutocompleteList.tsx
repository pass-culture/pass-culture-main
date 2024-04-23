import cx from 'classnames'
import React from 'react'

import strokeDownIcon from 'icons/stroke-down.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './AutocompleteList.module.scss'
import { AutocompleteItemProps } from './type'

// FIXME (MathildeDuboille - 15-06-22): improve accessibility and refactor if needed.
// This component is used in SelectAutocomplete and MultiselectAutocomplete
type AutocompleteListProps = {
  className?: string
  displayNumberOfSelectedValues?: boolean
  filteredOptions: AutocompleteItemProps[]
  isOpen: boolean
  maxHeight?: number
  numberOfSelectedOptions?: number
  onButtonClick: () => void
  renderOption: (option: AutocompleteItemProps) => React.ReactNode
  disabled?: boolean
  hideArrow?: boolean
}

export const AutocompleteList = ({
  isOpen,
  onButtonClick,
  filteredOptions,
  maxHeight,
  renderOption,
  displayNumberOfSelectedValues = false,
  numberOfSelectedOptions,
  className,
  disabled,
  hideArrow = false,
}: AutocompleteListProps): JSX.Element => {
  return (
    <div className={styles['field-overlay']}>
      {!hideArrow && (
        <button
          onClick={onButtonClick}
          className={styles['dropdown-indicator']}
          type="button"
          disabled={disabled}
        >
          <SvgIcon
            src={strokeDownIcon}
            alt={`${isOpen ? 'Masquer' : 'Afficher'} les options`}
            width="20"
          />
        </button>
      )}
      {displayNumberOfSelectedValues && (
        <div onClick={onButtonClick} className={styles['pellet']}>
          {numberOfSelectedOptions}
        </div>
      )}
      {isOpen && (
        <div
          className={cx(styles['menu'], className)}
          style={maxHeight ? { maxHeight } : {}}
          role="listbox"
        >
          {filteredOptions.length === 0 && (
            <span className={styles['menu--no-results']}>Aucun résultat</span>
          )}
          {filteredOptions.map((option) => renderOption(option))}
        </div>
      )}
    </div>
  )
}
