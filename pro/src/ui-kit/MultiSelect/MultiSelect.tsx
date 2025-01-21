import { useEffect, useId, useRef, useState } from 'react'

import { useOnClickOrFocusOutside } from 'commons/hooks/useOnClickOrFocusOutside'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

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
  hasSelectAllOptions?: boolean
  disabled?: boolean
  onSelectedOptionsChanged: (options: Option[]) => void
  error?: string
  name: string
  buttonLabel: string
} & ( // If `hasSearch` is `true`, `searchLabel` are required. // This part applies the condition
  | { hasSearch: true; searchLabel: string }
  // If `hasSearch` is `false` or undefined, `searchLabel` are optional.
  | {
      hasSearch?: false | undefined
      searchLabel?: never
    }
)

export const MultiSelect = ({
  options,
  defaultOptions = [],
  hasSearch = false,
  searchLabel,
  label,
  hasSelectAllOptions,
  disabled,
  onSelectedOptionsChanged,
  error,
  name,
  buttonLabel,
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
    onSelectedOptionsChanged(updatedSelectedItems)
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
    <FieldLayout label={label} name={name} error={error} showError={!!error}>
      <fieldset className={styles.container} ref={containerRef}>
        <MultiSelectTrigger
          id={id}
          buttonLabel={buttonLabel}
          fieldLabel={label}
          isOpen={isOpen}
          toggleDropdown={toggleDropdown}
          selectedCount={selectedItems.length}
          disabled={disabled}
          error={error}
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
    </FieldLayout>
  )
}
