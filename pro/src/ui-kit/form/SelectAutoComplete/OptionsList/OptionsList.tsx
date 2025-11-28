import cx from 'classnames'
import type { Ref } from 'react'

import type { SelectOption } from '@/commons/custom_types/form'

import styles from './OptionsList.module.scss'

export interface OptionsListProps {
  className?: string
  fieldName: string
  filteredOptions: SelectOption[]
  setHoveredOptionIndex: (value: number | null) => void
  listRef: Ref<HTMLUListElement>
  hoveredOptionIndex: number | null
  selectOption: (value: string) => void
}

export const OptionsList = ({
  className,
  fieldName,
  filteredOptions,
  setHoveredOptionIndex,
  listRef,
  hoveredOptionIndex,
  selectOption,
}: OptionsListProps): JSX.Element => (
  <ul
    className={cx(styles['menu'], className)}
    data-testid="list"
    id={`list-${fieldName}`}
    ref={listRef}
    role="listbox"
    aria-label="options"
  >
    {filteredOptions.length > 0 ? (
      filteredOptions.map(({ value, label }: SelectOption, index: number) => {
        const isSelected = hoveredOptionIndex === index
        return (
          // biome-ignore lint/a11y/useKeyWithClickEvents: the onKeyDown is handled in the parent component
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
            onClick={() => {
              selectOption(value)
            }}
            role="option"
            tabIndex={-1}
          >
            <span className={cx(styles['options-item'])}>{label}</span>
          </li>
        )
      })
    ) : (
      <li className={styles['menu--no-results']}>Aucun résultat</li>
    )}
  </ul>
)
