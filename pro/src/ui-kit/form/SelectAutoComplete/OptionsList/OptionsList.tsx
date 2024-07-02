import cx from 'classnames'
import React, { Ref } from 'react'

import { SelectOption } from 'custom_types/form'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import baseCheckboxStyles from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox.module.scss'
import { pluralize } from 'utils/pluralize'

import styles from './OptionsList.module.scss'

interface OptionsListProps {
  className?: string
  fieldName: string
  selectedValues: string | string[] | null
  filteredOptions: SelectOption[]
  setHoveredOptionIndex: (value: number | null) => void
  listRef: Ref<HTMLUListElement>
  hoveredOptionIndex: number | null
  selectOption: (value: string) => void
  multi: boolean
  maxDisplayedOptions?: number
}

export const OptionsList = ({
  className,
  fieldName,
  selectedValues,
  filteredOptions,
  setHoveredOptionIndex,
  listRef,
  hoveredOptionIndex,
  selectOption,
  multi,
  maxDisplayedOptions,
}: OptionsListProps): JSX.Element => {
  const displayedOptions = maxDisplayedOptions
    ? filteredOptions.slice(0, maxDisplayedOptions)
    : filteredOptions

  return (
    <div className={cx(styles['menu'], className)} role="listbox">
      {filteredOptions.length === 0 && (
        <span className={styles['menu--no-results']}>Aucun résultat</span>
      )}
      <ul
        data-testid="list"
        id={`list-${fieldName}`}
        ref={listRef}
        role="listbox"
      >
        {displayedOptions.map(
          ({ value, label }: SelectOption, index: number) => {
            const isSelected = (selectedValues || []).includes(String(value))
            return (
              <li
                aria-selected={isSelected}
                aria-posinset={index + 1}
                aria-setsize={displayedOptions.length}
                className={
                  hoveredOptionIndex === index ? styles['option-hovered'] : ''
                }
                data-value={value}
                data-selected={isSelected}
                id={`option-display-${value}`}
                key={`option-display-${value}`}
                onMouseEnter={() => setHoveredOptionIndex(index)}
                role="option"
                tabIndex={-1}
              >
                {multi ? (
                  <BaseCheckbox
                    label={label}
                    checked={isSelected}
                    onChange={() => {
                      selectOption(String(value))
                    }}
                  />
                ) : (
                  <span
                    onClick={() => {
                      selectOption(String(value))
                    }}
                    className={cx(
                      baseCheckboxStyles['base-checkbox-label'],
                      styles['label']
                    )}
                  >
                    {label}
                  </span>
                )}
              </li>
            )
          }
        )}
      </ul>
      <div role="status">
        {maxDisplayedOptions &&
          displayedOptions.length < filteredOptions.length && (
            <div className={styles['too-many-options']}>
              {pluralize(maxDisplayedOptions, 'résultat')} maximum. Veuillez
              affiner votre recherche
            </div>
          )}
      </div>
    </div>
  )
}
