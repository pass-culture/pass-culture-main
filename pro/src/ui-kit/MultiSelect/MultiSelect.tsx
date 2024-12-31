import { useEffect, useId, useRef, useState } from 'react'

import { useOnClickOrFocusOutside } from 'commons/hooks/useOnClickOrFocusOutside'

import { SelectedValuesTags } from '../SelectedValuesTags/SelectedValuesTags'

import styles from './MultiSelect.module.scss'
import { MultiSelectPanel } from './MultiSelectPanel'
import { MultiSelectTrigger } from './MultiSelectTrigger'

export type Option = {
  id: string
  label: string
}

type MultiSelectProps = {
  options: Option[]
  defaultOptions?: Option[]
  label: string
  legend: string
  hasSelectAllOptions?: boolean
  disabled?: boolean
} & ( // If `hasSearch` is `true`, `searchExample` and `searchLabel` are required. // This part applies the condition
  | { hasSearch: true; searchExample: string; searchLabel: string }
  // If `hasSearch` is `false` or undefined, `searchExample` and `searchLabel` are optional.
  | {
      hasSearch?: false | undefined
      searchExample?: never
      searchLabel?: never
    }
)

export const MultiSelect = ({
  options,
  defaultOptions = [],
  hasSearch = false,
  searchExample,
  searchLabel,
  label,
  legend,
  hasSelectAllOptions,
  disabled,
}: MultiSelectProps): JSX.Element => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedItems, setSelectedItems] = useState<Option[]>(defaultOptions)
  const isSelectAllChecked = selectedItems.length === options.length

  const containerRef = useRef<HTMLFieldSetElement>(null)
  const id = useId()

  const toggleDropdown = () => setIsOpen((prev) => !prev)

  const handleSelectItem = (item: Option) => {
    const updatedSelectedItems = selectedItems.some((i) => i.id === item.id)
      ? selectedItems.filter((i) => i.id !== item.id)
      : [...selectedItems, item]

    setSelectedItems(updatedSelectedItems)
  }

  const handleSelectAll = () => {
    const updatedItems = isSelectAllChecked ? [] : options
    setSelectedItems(updatedItems)
  }

  const handleRemoveTag = (itemId: string) => {
    const updatedItems = selectedItems.filter((item) => item.id !== itemId)
    setSelectedItems(updatedItems)
  }

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      setIsOpen(false)
    }
  }

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [])

  useOnClickOrFocusOutside(containerRef, () => setIsOpen(false))

  return (
    <fieldset className={styles.container} ref={containerRef}>
      <MultiSelectTrigger
        id={id}
        legend={legend}
        label={label}
        isOpen={isOpen}
        toggleDropdown={toggleDropdown}
        selectedCount={selectedItems.length}
        disabled={disabled}
      />

      {isOpen && (
        <MultiSelectPanel
          id={id}
          label={label}
          options={options.map((option) => ({
            ...option,
            checked: selectedItems.some((item) => item.id === option.id),
          }))}
          onOptionSelect={handleSelectItem}
          onSelectAll={handleSelectAll}
          isAllChecked={isSelectAllChecked}
          hasSearch={hasSearch}
          searchExample={searchExample}
          searchLabel={searchLabel}
          hasSelectAllOptions={hasSelectAllOptions}
        />
      )}

      <SelectedValuesTags
        disabled={false}
        selectedOptions={selectedItems.map((item) => item.id)}
        removeOption={handleRemoveTag}
        fieldName="tags"
        optionsLabelById={selectedItems.reduce(
          (acc, item) => ({ ...acc, [item.id]: item.label }),
          {}
        )}
      />
    </fieldset>
  )
}
