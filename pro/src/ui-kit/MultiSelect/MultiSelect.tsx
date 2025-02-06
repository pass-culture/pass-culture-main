import { useEffect, useId, useRef, useState } from 'react'

import { useOnClickOrFocusOutside } from 'commons/hooks/useOnClickOrFocusOutside'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import { SelectedValuesTags } from '../SelectedValuesTags/SelectedValuesTags'

import styles from './MultiSelect.module.scss'
import { MultiSelectPanel } from './MultiSelectPanel'
import { MultiSelectTrigger } from './MultiSelectTrigger'

/**
 * Represents an option in the MultiSelect component.
 */
export type Option = {
  /** Unique identifier for the option */
  id: string
  /** Display label for the option */
  label: string
}

export interface Options {
  options: Option[]
  selectAllLabel?: string
  hasSelectAllOptions?: boolean
  checked?: boolean
}

/**
 * Props for the MultiSelect component.
 */
type MultiSelectProps = {
  /** Array of available options */
  options: Options[]
  /** Array of initially selected options */
  defaultOptions?: Option[]
  /** Label for the MultiSelect field */
  label: string
  /** Whether to include a "Select All" option */
  hasSelectAllOptions?: boolean
  /** Whether the MultiSelect is disabled */
  disabled?: boolean
  /** Callback function called when selected options change */
  onSelectedOptionsChanged: (options: Option[]) => void
  /** Error message to display */
  error?: string
  /** Name attribute for the form field */
  name: string
  /** Label for the dropdown button */
  buttonLabel: string
  isOptional?: boolean
} & (
  | {
      /**
       * Whether to include a search bar above options
       * If `hasSearch` is `true`, `searchLabel` are required. This part applies the condition
       */
      hasSearch: true
      searchLabel: string
    }
  /* If `hasSearch` is `false` or undefined, `searchLabel` should not be provided. */
  | {
      hasSearch?: false | undefined
      searchLabel?: never
    }
)

/**
 * MultiSelect component for selecting multiple options from a dropdown list.
 *
 * This component provides a customizable dropdown for selecting multiple options,
 * with features like search functionality, select all option, and individual option selection.
 * It integrates with form layouts.
 *
 * @param {MultiSelectProps} props - The props for the MultiSelect component.
 * @returns {JSX.Element} The rendered MultiSelect component.
 *
 * @example
 * <MultiSelect
 *   options={[
 *     { id: '1', label: 'Option 1' },
 *     { id: '2', label: 'Option 2' },
 *     { id: '3', label: 'Option 3' }
 *   ]}
 *   label="Select Options"
 *   buttonLabel="Options"
 *   name="multiSelect"
 *   onSelectedOptionsChanged={(selectedOptions) => console.log(selectedOptions)}
 *   hasSearch={true}
 *   searchLabel="Search options"
 * />
 *
 *
 * @accessibility
 * - The component uses `aria-expanded` to indicate the open/closed state of the dropdown.
 * - The dropdown trigger is keyboard accessible and can be activated using Enter or Space.
 * - When open, the dropdown panel is navigable using arrow keys.
 *
 */
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
  isOptional = false,
}: MultiSelectProps): JSX.Element => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedItems, setSelectedItems] = useState<Option[]>(defaultOptions)
  const [checkboxStates, setCheckboxStates] = useState(() => {
    return options.reduce(
      (acc, group, index) => {
        if (group.hasSelectAllOptions) {
          acc[index] = group.checked || false
        }
        return acc
      },
      {} as Record<number, boolean>
    )
  })

  const totalOptionsCount = options.reduce(
    (total, group) => total + group.options.length,
    0
  )

  const isSelectAllChecked = selectedItems.length === totalOptionsCount

  const mergedOptions = options.reduce(
    (acc, group) => [...acc, ...group.options],
    [] as Option[]
  )

  const containerRef = useRef<HTMLDivElement>(null)
  const id = useId()

  const toggleDropdown = () => setIsOpen((prev) => !prev)

  function updateSelectedItems(updatedSelectedItems: Option[]) {
    setSelectedItems(updatedSelectedItems)
    onSelectedOptionsChanged(updatedSelectedItems)
  }

  const handleSelectItem = (item: Option) => {
    const updatedItems = selectedItems.some((i) => i.id === item.id)
      ? selectedItems.filter((i) => i.id !== item.id)
      : [...selectedItems, item]

      options.forEach((group, index) => {
        if (group.options.some((opt) => opt.id === item.id)) {
          const allGroupItemsSelected = group.options.every(groupItem => 
            updatedItems.some(selectedItem => selectedItem.id === groupItem.id)
          )
    
          setCheckboxStates((prev) => ({
            ...prev,
            [index]: allGroupItemsSelected,
          }))
        }
      })

    updateSelectedItems(updatedItems)
  }

  const handleSelectAll = (option: Option[], index?: number) => {
    if (index !== undefined) {
      setCheckboxStates((prev) => ({
        ...prev,
        [index]: !prev[index],
      }))

      const optionIds = new Set(option.map((opt) => opt.id))
      const remainingItems = selectedItems.filter(
        (item) => !optionIds.has(item.id)
      )

      const mergedItems = [...selectedItems, ...option].filter(
        (item, index, self) => index === self.findIndex((t) => t.id === item.id)
      )

      updateSelectedItems(checkboxStates[index] ? remainingItems : mergedItems)
    } else {
      const updatedItems = isSelectAllChecked ? [] : option
      setCheckboxStates((prev) =>
        Object.keys(prev).reduce(
          (acc, key) => ({
            ...acc,
            [key]: isSelectAllChecked ? false : true,
          }),
          {}
        )
      )
      updateSelectedItems(updatedItems)
    }
  }

  const handleRemoveTag = (itemId: string) => {
    const updatedItems = selectedItems.filter((item) => item.id !== itemId)
    updateSelectedItems(updatedItems)
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
    <FieldLayout
      label={label}
      name={name}
      error={error}
      showError={!!error}
      isOptional={isOptional}
    >
      <fieldset className={styles.container}>
        <div ref={containerRef}>
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
              mergedOptions={mergedOptions.map((option) => ({
                ...option,
                checked: selectedItems.some((item) => item.id === option.id),
              }))}
              options={options}
              onOptionSelect={handleSelectItem}
              onSelectAllOptions={handleSelectAll}
              checkboxStates={checkboxStates}
              isAllChecked={isSelectAllChecked}
              hasSearch={hasSearch}
              searchLabel={searchLabel}
              hasSelectAllOptions={hasSelectAllOptions}
            />
          )}
        </div>

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
