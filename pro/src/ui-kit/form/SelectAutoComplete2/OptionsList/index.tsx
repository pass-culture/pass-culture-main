import cx from 'classnames'
import React, { Ref } from 'react'

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
          ({ value, label }: SelectOption, index: number) => (
            <li
              aria-selected={selectedValues.includes(value) ? 'true' : 'false'}
              aria-posinset={index + 1}
              aria-setsize={filteredOptions.length}
              className={`${
                selectedValues.includes(value) ? styles['option-selected'] : ''
              } ${hovered === index ? styles['option-hovered'] : ''}`}
              data-value={value}
              data-selected={selectedValues.includes(value)}
              id={`option-display-${value}`}
              key={`option-display-${value}`}
              onClick={() => {
                selectOption(value)
              }}
              onMouseEnter={() => setHovered(index)}
              role="option"
              tabIndex={-1}
            >
              {label}
            </li>
          )
        )}
      </ul>
    </div>
  )
}

export default OptionsList
