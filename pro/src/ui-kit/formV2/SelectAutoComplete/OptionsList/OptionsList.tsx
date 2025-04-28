import cx from 'classnames'
import { Ref } from 'react'

import { SelectOption } from 'commons/custom_types/form'

import styles from './OptionsList.module.scss'

export interface OptionsListProps {
  className?: string
  fieldName: string
  selectedValue: string | null
  filteredOptions: SelectOption[]
  setHoveredOptionIndex: (value: number | null) => void
  listRef: Ref<HTMLUListElement>
  hoveredOptionIndex: number | null
  selectOption: (value: string) => void
}

export const OptionsList = ({
  className,
  fieldName,
  selectedValue,
  filteredOptions,
  setHoveredOptionIndex,
  listRef,
  hoveredOptionIndex,
  selectOption,
}: OptionsListProps): JSX.Element => {
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
        {filteredOptions.map(
          ({ value, label }: SelectOption, index: number) => {
            const isSelected = selectedValue === String(value)
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
                onFocus={() => setHoveredOptionIndex(index)}
                role="option"
                tabIndex={-1}
              >
                <span
                  onClick={() => {
                    selectOption(String(value))
                  }}
                  className={cx(styles['options-item'])}
                >
                  {label}
                </span>
              </li>
            )
          }
        )}
      </ul>
    </div>
  )
}
