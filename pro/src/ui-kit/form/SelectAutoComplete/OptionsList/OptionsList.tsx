import cx from 'classnames'
import type { Ref } from 'react'

import type { SelectOption } from '@/commons/custom_types/form'
import strokeUserIcon from '@/icons/stroke-user.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './OptionsList.module.scss'

export interface OptionsListProps {
  className?: string
  fieldName: string
  filteredOptions: SelectOption[]
  setHoveredOptionIndex: (value: number | null) => void
  listRef: Ref<HTMLUListElement>
  hoveredOptionIndex: number | null
  selectOption: (option: SelectOption) => void
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
    // biome-ignore lint/a11y/noNoninteractiveElementToInteractiveRole: Seems to be the only solution for combobox pattern
    role="listbox"
    aria-label="options"
  >
    {filteredOptions.length > 0 ? (
      filteredOptions.map((option: SelectOption, index: number) => {
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
            data-value={option.value}
            data-selected={isSelected}
            id={`option-${fieldName}-${index}`}
            key={option.value}
            onMouseEnter={() => setHoveredOptionIndex(index)}
            onFocus={() => setHoveredOptionIndex(index)}
            onClick={() => {
              selectOption(option)
            }}
            // biome-ignore lint/a11y/noNoninteractiveElementToInteractiveRole: Seems to be the only solution for combobox pattern
            role="option"
            tabIndex={-1}
          >
            <span className={styles['options-item']}>
              {option.thumbUrl ? (
                <img
                  className={styles['options-img']}
                  alt=""
                  src={option.thumbUrl}
                />
              ) : (
                <span className={styles['options-placeholder-container']}>
                  <SvgIcon src={strokeUserIcon} alt="" width="20" />
                </span>
              )}
              <span>{option.label}</span>
            </span>
          </li>
        )
      })
    ) : (
      <li className={styles['menu--no-results']}>Aucun résultat</li>
    )}
  </ul>
)
