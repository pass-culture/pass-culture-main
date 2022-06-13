import Icon from 'components/layout/Icon'
import React from 'react'
import { SelectOption } from 'custom_types/form'
import cx from 'classnames'
import styles from './AutocompleteList.module.scss'

type AutocompleteListProps = {
  isOpen: boolean
  onButtonClick: () => void
  filteredOptions: (SelectOption & {disabled?: boolean})[]
  renderOption: (option: (SelectOption & {disabled?: boolean})) => React.ReactNode
  displayNumberOfSelectedValues?: boolean
  numberOfSelectedOptions?: number
}

const AutocompleteList = ({
  isOpen,
  onButtonClick,
  filteredOptions,
  renderOption,
  displayNumberOfSelectedValues = false,
  numberOfSelectedOptions,
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
        <div className={styles['menu']} role="listbox">
          {filteredOptions.length === 0 && (
            <span
              className={cx({
                [styles['menu--no-results']]:
                  filteredOptions.length === 0,
              })}
            >
              Aucun résultat
            </span>
          )}
          {filteredOptions.map((option) => renderOption(option))}
        </div>
      )}
    </div>
  )
}

export default AutocompleteList
