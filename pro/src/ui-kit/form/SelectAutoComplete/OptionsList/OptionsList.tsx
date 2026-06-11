import cx from 'classnames'
import fullMoreIcon from 'icons/full-more.svg'
import { type ReactNode, type Ref, useState } from 'react'

import type { SelectOption } from '@/commons/custom_types/form'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

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
  createOption: (option: string) => void
  creatableOption?: string
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
  createOption,
  creatableOption,
}: OptionsListProps): JSX.Element => {
  const optionListSize = filteredOptions.length + (creatableOption ? 1 : 0)
  return (
    <ul
      className={cx(styles['menu'], className)}
      data-testid="list"
      id={`list-${fieldName}`}
      ref={listRef}
      // biome-ignore lint/a11y/noNoninteractiveElementToInteractiveRole: Seems to be the only solution for combobox pattern
      role="listbox"
      aria-label="options"
      onMouseDown={(e) => e.preventDefault()}
    >
      {creatableOption && (
        <OptionListItem
          key={creatableOption}
          fieldName={fieldName}
          index={0}
          optionListSize={optionListSize}
          isHovered={hoveredOptionIndex === 0}
          dataValue={creatableOption}
          setHoveredOptionIndex={setHoveredOptionIndex}
          onClick={() => createOption(creatableOption)}
        >
          <CreatableOptionItem
            label={creatableOption}
            withSeparator={optionListSize > 1}
          />
        </OptionListItem>
      )}
      {filteredOptions.map((option: SelectOption, index: number) => {
        const realIndex = creatableOption ? index + 1 : index
        return (
          <OptionListItem
            key={option.value}
            fieldName={fieldName}
            index={realIndex}
            optionListSize={optionListSize}
            isHovered={hoveredOptionIndex === realIndex}
            dataValue={option.value}
            setHoveredOptionIndex={setHoveredOptionIndex}
            onClick={() => selectOption(option)}
          >
            <OptionItem
              label={option.label}
              description={option.description}
              thumbUrl={option.thumbUrl}
              thumbPlaceholder={thumbPlaceholder}
            />
          </OptionListItem>
        )
      })}
      {optionListSize === 0 && (
        <li className={styles['menu--no-results']}>Aucun résultat</li>
      )}
    </ul>
  )
}

interface OptionListItemProps {
  fieldName: string
  index: number
  optionListSize: number
  isHovered: boolean
  dataValue: string | number
  setHoveredOptionIndex: (value: number | null) => void
  onClick: () => void
  children: ReactNode
}

const OptionListItem = ({
  fieldName,
  index,
  optionListSize,
  isHovered,
  dataValue,
  setHoveredOptionIndex,
  onClick,
  children,
}: OptionListItemProps) => (
  // biome-ignore lint/a11y/useKeyWithClickEvents: the onKeyDown is handled in the parent component
  <li
    aria-selected={isHovered}
    aria-posinset={index + 1}
    aria-setsize={optionListSize}
    className={isHovered ? styles['option-hovered'] : ''}
    data-value={dataValue}
    data-selected={isHovered}
    id={`option-${fieldName}-${index}`}
    onMouseEnter={() => setHoveredOptionIndex(index)}
    onFocus={() => setHoveredOptionIndex(index)}
    onClick={onClick}
    // biome-ignore lint/a11y/noNoninteractiveElementToInteractiveRole: Seems to be the only solution for combobox pattern
    role="option"
    tabIndex={-1}
  >
    <div className={styles['option-item-wrapper']}>{children}</div>
  </li>
)

const CreatableOptionItem = ({
  label,
  withSeparator,
}: {
  label: string
  withSeparator: boolean
}) => (
  <span
    className={cx(
      styles['options-item'],
      withSeparator && styles['options-item--separator']
    )}
  >
    <SvgIcon
      src={fullMoreIcon}
      alt={`Ajouter ${label}`}
      width="20"
      className={styles['option-creatable-icon']}
    />
    <span className={styles['option-creatable-label']} aria-hidden="true">
      Ajouter &quot;{label}&quot;
    </span>
  </span>
)

const OptionItem = ({
  label,
  description,
  thumbUrl,
  thumbPlaceholder,
}: {
  label: string
  description?: string | null
  thumbUrl?: string | null
  thumbPlaceholder?: string
}) => (
  <span className={styles['options-item']}>
    {(thumbUrl || thumbPlaceholder) && (
      <ThumbWithPlaceholder
        thumbUrl={thumbUrl}
        thumbPlaceholder={thumbPlaceholder}
      />
    )}
    <span className={styles['option-texts']}>
      <span>{label}</span>
      {description && (
        <span className={styles['option-description']}>{description}</span>
      )}
    </span>
  </span>
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
