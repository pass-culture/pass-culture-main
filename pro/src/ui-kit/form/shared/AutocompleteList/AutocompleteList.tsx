import Icon from 'components/layout/Icon'
import React from 'react'
import { SelectOption } from 'custom_types/form'
import cx from 'classnames'
import styles from './AutocompleteList.module.scss'

// FIXME (MathildeDuboille - 15-06-22): improve accessibility and refactor if needed.
// This component is used in SelectAutocomplete and MultiselectAutocomplete
type AutocompleteListProps = {
  isOpen: boolean
  onButtonClick: () => void
  filteredOptions: (SelectOption & { disabled?: boolean })[]
  renderOption: (
    option: SelectOption & { disabled?: boolean }
  ) => React.ReactNode
  displayNumberOfSelectedValues?: boolean
  numberOfSelectedOptions?: number
  className?: string
}

const AutocompleteList = ({
  isOpen,
  onButtonClick,
  filteredOptions,
  renderOption,
  displayNumberOfSelectedValues = false,
  numberOfSelectedOptions,
  className,
}: AutocompleteListProps): JSX.Element => {
  return (
    <div className={styles['field-overlay']}>
      <button
        onClick={onButtonClick}
        className={cx(styles['dropdown-indicator'], {
          [styles['dropdown-indicator-is-closed']]: !isOpen,
        })}
        type="button"
      >
        <Icon
          svg="open-dropdown"
          alt={`${isOpen ? 'Masquer' : 'Afficher'} les options`}
        />
      </button>
      {displayNumberOfSelectedValues && (
        <div onClick={onButtonClick} className={styles['pellet']}>
          {numberOfSelectedOptions}
        </div>
      )}
      {isOpen && (
        <div className={cx(styles['menu'], className)} role="listbox">
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
