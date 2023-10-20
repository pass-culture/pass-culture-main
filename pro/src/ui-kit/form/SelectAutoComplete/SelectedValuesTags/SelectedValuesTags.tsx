import cn from 'classnames'
import React from 'react'

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
  return (
    <div className={styles['multi-select-autocomplete-tags']}>
      {selectedOptions.map((value: string) => (
        <span key={`tag-${fieldName}-${value}`} className={styles['tag']}>
          <button
            className={cn(styles['tag-close-button'], {
              [styles['tag-close-button--disabled']]: disabled,
            })}
            onClick={() => removeOption(value)}
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
        </span>
      ))}
    </div>
  )
}
