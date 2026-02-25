import cx from 'classnames'
import { type Ref, useState } from 'react'

import type { SelectOption } from '@/commons/custom_types/form'

import styles from './OptionsList.module.scss'

export interface OptionsListProps {
  className?: string
  fieldName: string
  filteredOptions: SelectOption[]
  thumbPlaceholder?: string
  setHoveredOptionIndex: (value: number | null) => void
  listRef: Ref<HTMLUListElement>
  hoveredOptionIndex: number | null
  selectOption: (option: SelectOption) => void
}

export const OptionsList = ({
  className,
  fieldName,
  filteredOptions,
  thumbPlaceholder,
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
              {(option.thumbUrl || thumbPlaceholder) && (
                <ThumbWithPlaceholder
                  thumbUrl={option.thumbUrl}
                  thumbPlaceholder={thumbPlaceholder}
                />
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

const ThumbWithPlaceholder = ({
  thumbUrl,
  thumbPlaceholder,
}: {
  thumbUrl?: string | null
  thumbPlaceholder?: string
}) => {
  const [isLoaded, setIsLoaded] = useState(false)

  return (
    <span className={styles['options-img-wrapper']}>
      {thumbPlaceholder && (
        <img
          className={styles['options-img']}
          alt=""
          src={thumbPlaceholder}
          aria-hidden={true}
        />
      )}
      {thumbUrl && (
        <img
          className={cx(
            styles['options-img'],
            styles['options-img-hidden'],
            isLoaded && styles['options-img-visible']
          )}
          alt=""
          src={thumbUrl}
          aria-hidden={true}
          onLoad={() => setIsLoaded(true)}
          onError={() => setIsLoaded(false)}
        />
      )}
    </span>
  )
}
