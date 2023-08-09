import cx from 'classnames'
import React, { Ref } from 'react'

import { SelectOption } from 'custom_types/form'
import BaseCheckbox from 'ui-kit/form/shared/BaseCheckbox'
import baseCheckboxStyles from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox.module.scss'

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
}

const OptionsList = ({
  className,
  fieldName,
  selectedValues,
  filteredOptions,
  setHoveredOptionIndex,
  listRef,
  hoveredOptionIndex,
  selectOption,
  multi,
}: OptionsListProps): JSX.Element => {
  return (
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
      <ul
        data-testid="list"
        id={`list-${fieldName}`}
        ref={listRef}
        role="listbox"
      >
        {filteredOptions.map(
          ({ value, label }: SelectOption, index: number) => {
            const isSelected = (selectedValues || []).includes(String(value))
            return (
              <li
                aria-selected={isSelected}
                aria-posinset={index + 1}
                aria-setsize={filteredOptions.length}
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
    </div>
  )
}

export default OptionsList
