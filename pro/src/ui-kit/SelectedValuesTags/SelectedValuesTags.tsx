import cn from 'classnames'
import { useRef } from 'react'

import fullCloseIcon from '@/icons/full-close.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SelectedValuesTags.module.scss'

interface TagsProps {
  disabled: boolean
  fieldName: string
  optionsLabelById: Record<string, string>
  selectedOptions: string[]
  removeOption: (value: string) => void
  className?: string
}

export const SelectedValuesTags = ({
  disabled,
  fieldName,
  optionsLabelById,
  selectedOptions,
  removeOption,
  className,
}: TagsProps): JSX.Element | null => {
  const tagListRef = useRef<HTMLUListElement>(null)

  function onTagRemoved(tag: string, index: number) {
    const listElements = tagListRef.current?.getElementsByTagName('button')
    const nextElement = listElements?.[index + 1] || listElements?.[index - 1]

    nextElement?.focus()
    removeOption(tag)
  }

  const visibleTags = selectedOptions.slice(0, 5)
  const extraTagsCount = selectedOptions.length - visibleTags.length

  if (selectedOptions.length === 0) {
    return null
  }

  return (
    <ul className={cn(styles['selected-tags'], className)} ref={tagListRef}>
      {visibleTags.map((value: string, i) => (
        <li key={`tag-${fieldName}-${value}`}>
          <button
            aria-label={`Supprimer ${optionsLabelById[value]}`}
            className={styles['tag-button']}
            onClick={() => onTagRemoved(value, i)}
            type="button"
            disabled={disabled}
          >
            {optionsLabelById[value]}
            <SvgIcon
              src={fullCloseIcon}
              alt="Fermer"
              className={styles['tag-button-icon']}
            />
          </button>
        </li>
      ))}

      {/* If there are more than 5 tags, display a tag for the extra options */}
      {extraTagsCount > 0 && (
        <li className={styles['tag-extra-count']}>+{extraTagsCount}...</li>
      )}
    </ul>
  )
}
