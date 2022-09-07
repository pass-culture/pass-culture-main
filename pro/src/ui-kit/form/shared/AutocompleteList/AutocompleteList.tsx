import cx from 'classnames'
import React from 'react'

import Icon from 'components/layout/Icon'

import styles from './AutocompleteList.module.scss'
import { IAutocompleteItemProps } from './type'

// FIXME (MathildeDuboille - 15-06-22): improve accessibility and refactor if needed.
// This component is used in SelectAutocomplete and MultiselectAutocomplete
type AutocompleteListProps = {
  className?: string
  displayNumberOfSelectedValues?: boolean
  filteredOptions: IAutocompleteItemProps[]
  isOpen: boolean
  maxHeight?: number
  numberOfSelectedOptions?: number
  onButtonClick: () => void
  renderOption: (option: IAutocompleteItemProps) => React.ReactNode
  disabled?: boolean
  hideArrow?: boolean
}

const AutocompleteList = ({
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
          className={cx(styles['dropdown-indicator'], {
            [styles['dropdown-indicator-is-closed']]: !isOpen,
          })}
          type="button"
          disabled={disabled}
        >
          <Icon
            svg="open-dropdown"
            alt={`${isOpen ? 'Masquer' : 'Afficher'} les options`}
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
            <span
              className={cx({
                [styles['menu--no-results']]: filteredOptions.length === 0,
              })}
            >
              Aucun résultat
            </span>
          )}
          {filteredOptions.map(option => renderOption(option))}
        </div>
      )}
    </div>
  )
}

export default AutocompleteList
