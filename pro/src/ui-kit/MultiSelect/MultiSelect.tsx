import cn from 'classnames'
import {
  ForwardedRef,
  forwardRef,
  useEffect,
  useId,
  useRef,
  useState,
} from 'react'

import { useOnClickOrFocusOutside } from 'commons/hooks/useOnClickOrFocusOutside'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'

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

/**
 * Props for the MultiSelect component.
 */
type MultiSelectProps = {
  /** Array of available options */
  options: Option[]
  /** Array of available options */
  selectedOptions?: Option[]
  /** Array of initially selected options */
  defaultOptions?: Option[]
  /** Label for the MultiSelect field */
  label: string
  /** Whether to include a "Select All" option */
  hasSelectAllOptions?: boolean
  /** Whether the MultiSelect is disabled */
  disabled?: boolean
  /** Callback function called when selected options change,
   *  Multiple selections can be made by selecting only one item (ex: selectInterventionAreas.ts)
   */
  onSelectedOptionsChanged: (
    selectedOptions: Option[],
    addedOptions: Option[],
    removedOptions: Option[]
  ) => void
  /** Error message to display */
  error?: string
  /** Name attribute for the form field */
  name: string
  /** Label for the dropdown button */
  buttonLabel: string
  /** field is required */
  required?: boolean
  /** display asterik  */
  asterisk?: boolean
  /** this class offers the possibility of limiting the size of the multiselect  */
  className?: string

  /** Trigger function to display error message when element is unfocus */
  onBlur?: () => void
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
 *   onSelectedOptionsChanged={({selectedOptions, addedOptions, removedOptions}) => console.log(selectedOptions, addedOptions, removedOptions)}
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
export const MultiSelect = forwardRef(
  (
    {
      className,
      options,
      selectedOptions,
      defaultOptions = [],
      hasSearch = false,
      searchLabel,
      label,
      hasSelectAllOptions,
      disabled = false,
      onSelectedOptionsChanged,
      error,
      name,
      buttonLabel,
      required = false,
      asterisk = true,
      onBlur,
    }: MultiSelectProps,
    forwardedRef: ForwardedRef<HTMLFieldSetElement>
  ): JSX.Element => {
    const [isOpen, setIsOpen] = useState(false)
    const [selectedItems, setSelectedItems] = useState<Option[]>(defaultOptions)
    const isSelectAllChecked = selectedItems.length === options.length

    const containerRef = useRef<HTMLDivElement>(null)
    const id = useId()

    const toggleDropdown = () => setIsOpen((prev) => !prev)

    useEffect(() => {
      if (selectedOptions) {
        setSelectedItems(selectedOptions)
      }
    }, [selectedOptions])

    function updateSelectedItems(updatedSelectedItems: Option[]) {
      const currentIds = new Set(selectedItems.map((item) => item.id))
      const updatedIds = new Set(updatedSelectedItems.map((item) => item.id))

      const removedOptionsIds = new Set(
        [...currentIds].filter((id) => !updatedIds.has(id))
      )

      const addedOptionsIds = new Set(
        [...updatedIds].filter((id) => !currentIds.has(id))
      )

      onSelectedOptionsChanged(
        updatedSelectedItems,
        options.filter((op) => addedOptionsIds.has(op.id)),
        options.filter((op) => removedOptionsIds.has(op.id))
      )
      setSelectedItems(updatedSelectedItems)
    }

    const handleSelectItem = (item: Option) => {
      const updatedItems = selectedItems.some((i) => i.id === item.id)
        ? selectedItems.filter((i) => i.id !== item.id)
        : [...selectedItems, item]

      updateSelectedItems(updatedItems)
    }

    const handleSelectAll = () => {
      const updatedItems = isSelectAllChecked ? [] : options
      updateSelectedItems(updatedItems)
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
      <fieldset className={styles.container} onBlur={onBlur} ref={forwardedRef}>
        <legend className={styles['container-label']}>
          {label} {required && asterisk && '*'}
        </legend>
        <div className={cn(className, styles['container-input'])}>
          <div ref={containerRef}>
            <MultiSelectTrigger
              id={id}
              buttonLabel={buttonLabel}
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
          </div>
          <div role="alert" id={`error-details-${name}`}>
            {error && (
              <FieldError name={name} className={styles['field-error']}>
                {error}
              </FieldError>
            )}
          </div>
        </div>

        <SelectedValuesTags
          disabled={disabled}
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
)

MultiSelect.displayName = 'MultiSelect'
