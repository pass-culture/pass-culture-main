import cx from 'classnames'
import React, { Ref } from 'react'

import BaseCheckbox from 'ui-kit/form/shared/BaseCheckbox'
import baseCheckboxStyles from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox.module.scss'

import styles from './OptionsList.module.scss'

type SelectOption = { value: string; label: string }

export interface OptionsListProps {
  className?: string
  fieldName: string
  maxHeight?: number
  selectedValues: string | string[]
  filteredOptions: SelectOption[]
  setHovered: (value: number | null) => void
  listRef: Ref<HTMLUListElement>
  hovered: number | null
  selectOption: (value: string) => void
  multi: boolean
}

const OptionsList = ({
  className,
  fieldName,
  maxHeight,
  selectedValues,
  filteredOptions,
  setHovered,
  listRef,
  hovered,
  selectOption,
  multi,
}: OptionsListProps): JSX.Element => {
  return (
    <div
      className={cx(styles['menu'], className)}
      style={
        /* istanbul ignore next: graphic variation */ maxHeight
          ? { maxHeight }
          : {}
      }
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
      <ul
        data-testid="list"
        id={`list-${fieldName}`}
        ref={listRef}
        role="listbox"
      >
        {filteredOptions.map(
          ({ value, label }: SelectOption, index: number) => {
            const isSelected = selectedValues.includes(value)
            return (
              <li
                aria-selected={isSelected ? 'true' : 'false'}
                aria-posinset={index + 1}
                aria-setsize={filteredOptions.length}
                className={hovered === index ? styles['option-hovered'] : ''}
                data-value={value}
                data-selected={isSelected}
                id={`option-display-${value}`}
                key={`option-display-${value}`}
                onMouseEnter={() => setHovered(index)}
                role="option"
                tabIndex={-1}
              >
                {multi ? (
                  <BaseCheckbox
                    label={label}
                    checked={isSelected}
                    onChange={() => {
                      selectOption(value)
                    }}
                  />
                ) : (
                  <span
                    onClick={() => {
                      selectOption(value)
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
