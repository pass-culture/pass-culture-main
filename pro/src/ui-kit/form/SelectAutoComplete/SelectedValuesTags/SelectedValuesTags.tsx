import cn from 'classnames'
import { useRef } from 'react'

import strokeCloseIcon from 'icons/stroke-close.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SelectedValuesTags.module.scss'

interface TagsProps {
  disabled: boolean
  fieldName: string
  optionsLabelById: Record<string, string>
  selectedOptions: string[]
  removeOption: (value: string) => void
}

export const SelectedValuesTags = ({
  disabled,
  fieldName,
  optionsLabelById,
  selectedOptions,
  removeOption,
}: TagsProps): JSX.Element => {
  const tagListRef = useRef<HTMLUListElement>(null)

  function onTagRemoved(tag: string, index: number) {
    const listElements = tagListRef.current?.getElementsByTagName('button')
    //  When a tag is removed, focus to the next tag button if it exists or to the previous tag button if it exists
    if (listElements?.[index + 1]) {
      listElements[index + 1].focus()
    } else if (listElements?.[index - 1]) {
      listElements[index - 1].focus()
    }
    removeOption(tag)
  }

  return (
    <ul className={styles['multi-select-autocomplete-tags']} ref={tagListRef}>
      {selectedOptions.map((value: string, i) => (
        <li key={`tag-${fieldName}-${value}`} className={styles['tag']}>
          <button
            className={cn(styles['tag-close-button'], {
              [styles['tag-close-button--disabled']]: disabled,
            })}
            onClick={() => onTagRemoved(value, i)}
            title={'Supprimer ' + optionsLabelById[value]}
            type="button"
            disabled={disabled}
          >
            {optionsLabelById[value]}

            <SvgIcon
              src={strokeCloseIcon}
              alt={'Supprimer ' + optionsLabelById[value]}
              className={styles['tag-close-button-icon']}
            />
          </button>
        </li>
      ))}
    </ul>
  )
}
