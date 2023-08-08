import React from 'react'

import Tag from 'ui-kit/Tag'

import styles from './Tags.module.scss'

interface TagsProps {
  disabled: boolean
  fieldName: string
  optionsLabelById: Record<string, string>
  selectedOptions: string[]
  removeOption: (value: string) => void
}

const Tags = ({
  disabled,
  fieldName,
  optionsLabelById,
  selectedOptions,
  removeOption,
}: TagsProps): JSX.Element => {
  return (
    <div className={styles['multi-select-autocomplete-tags']}>
      {selectedOptions.map((value: string) => (
        <Tag
          key={`tag-${fieldName}-${value}`}
          label={optionsLabelById[value]}
          closeable={{
            closeLabel: 'Supprimer ' + optionsLabelById[value],
            onClose: () => {
              removeOption(value)
            },
            disabled,
          }}
        />
      ))}
    </div>
  )
}

export default Tags
