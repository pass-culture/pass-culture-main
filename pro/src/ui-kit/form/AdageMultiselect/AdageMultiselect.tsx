import { useCombobox } from 'downshift'
import { useEffect, useId, useState } from 'react'

import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import strokeSearch from '@/icons/stroke-search.svg'
import { BaseInput } from '@/ui-kit/form/shared/BaseInput/BaseInput'

import styles from './AdageMultiselect.module.scss'

export interface ItemProps {
  label: string
  value: number | string | string[]
}

interface AdageMultiselectProps {
  options: ItemProps[]
  name: string
  label: string
  isOpen: boolean
  selectedOptions?: ItemProps['value'][]
  onSelectedOptionsChanged: (selectedItems: ItemProps['value'][]) => void
  filterMaxLength?: number
  sortOptions?: (
    items: ItemProps[],
    selectedItems: ItemProps['value'][]
  ) => ItemProps[]
}

const filterItems = (items: ItemProps[], inputValue: string) => {
  const regExp = new RegExp(
    inputValue.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, ''),
    'i'
  )
  return items.filter((item) => item.label.match(regExp))
}

const defaultSortOptions = (
  items: ItemProps[],
  selectedItems: ItemProps['value'][]
) => {
  return items.sort((a, b) => {
    if (
      isIncluded(selectedItems, b.value) &&
      !isIncluded(selectedItems, a.value)
    ) {
      return 1
    }
    if (
      !isIncluded(selectedItems, b.value) &&
      isIncluded(selectedItems, a.value)
    ) {
      return -1
    }
    return a.label.localeCompare(b.label)
  })
}

const isIncluded = (
  fieldValue: ItemProps['value'][],
  value: ItemProps['value']
): boolean => {
  if (Array.isArray(value)) {
    const valueSet = new Set(value)
    return fieldValue.some(
      (fieldValueItem) =>
        Array.isArray(fieldValueItem) &&
        fieldValueItem.length === value.length &&
        fieldValueItem.every((val) => valueSet.has(val))
    )
  }

  return fieldValue.includes(value)
}

export const AdageMultiselect = ({
  options,
  name,
  label,
  isOpen,
  selectedOptions,
  onSelectedOptionsChanged,
  sortOptions,
  filterMaxLength = 255,
}: AdageMultiselectProps) => {
  // We need to maintain the input value in state so that we can use it in itemToString
  const [inputValue, setInputValue] = useState('')
  const [sortedOptions, setSortedOptions] = useState<ItemProps[]>([])
  const indicationId = useId()
  const [selectedItems, setSelectedItems] = useState<ItemProps['value'][]>([])

  useEffect(() => {
    if (selectedOptions) {
      setSelectedItems(selectedOptions)
    }
  }, [selectedOptions])

  const {
    getLabelProps,
    getMenuProps,
    getInputProps,
    getItemProps,
    setInputValue: setDownshiftInputValue,
  } = useCombobox({
    items: sortedOptions,
    defaultHighlightedIndex: 0, // after selection, highlight the first item.
    selectedItem: null,
    stateReducer(_state, actionAndChanges) {
      const { changes, type } = actionAndChanges
      /* istanbul ignore next: no need to test all case here, downshift behaviour */
      if (
        type === useCombobox.stateChangeTypes.InputKeyDownEnter ||
        type === useCombobox.stateChangeTypes.ItemClick
      ) {
        return {
          ...changes,
          // We force isOpen to true because we always want to display the list of options
          isOpen: true,
        }
      }
      return changes
    },
    onInputValueChange: ({ inputValue: newInputValue }) => {
      setInputValue(newInputValue || '')
    },
    // By default downshift will use this callback to display the selected item, we just want to always display the input value
    itemToString: () => inputValue,
  })

  const computeNewSelectedItems = (selection: ItemProps) => {
    if (isIncluded(selectedItems, selection.value)) {
      if (selectedItems.length > 0 && Array.isArray(selectedItems[0])) {
        return (selectedItems as string[][]).filter(
          (item) =>
            !(selection.value as string[]).some((el) => item.includes(el))
        )
      }
      return selectedItems.filter(
        (item) => !isIncluded([selection.value], item)
      )
    }
    return [...selectedItems, selection.value]
  }

  const handleNewSelection = (selection: ItemProps) => {
    const newSelectedItems = computeNewSelectedItems(selection)
    onSelectedOptionsChanged(newSelectedItems)
    setSelectedItems(newSelectedItems)
  }

  // The isOpen modal state is handle outside of the component, we want to clear the input and sort items on open/close
  useEffect(() => {
    setInputValue('')
    setDownshiftInputValue('')
    setSortedOptions(
      (sortOptions ?? defaultSortOptions)(options, selectedItems)
    )
  }, [isOpen])

  return (
    <div className={styles['container']}>
      <label
        htmlFor="search"
        className={styles['visually-hidden']}
        {...getLabelProps()}
      >
        {label}
      </label>
      <BaseInput
        type="search"
        name="search"
        className={styles['search-input']}
        maxLength={filterMaxLength}
        value={inputValue}
        aria-describedby={indicationId}
        leftIcon={strokeSearch}
        {...getInputProps()}
      />
      <ul
        className={styles['search-list']}
        {...getMenuProps({
          'aria-activedescendant': getInputProps()['aria-activedescendant'],
        })}
      >
        {filterItems(sortedOptions, inputValue).map((item, index) => {
          // we cannot pass down the ref to basecheckbox as it is a function component

          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          const { ref: _ref, ...itemProps } = getItemProps({ item, index })
          const liValueKey = Array.isArray(item.value)
            ? item.value.join('_')
            : item.value

          const isChecked = isIncluded(selectedItems, item.value)

          return (
            <li key={`${liValueKey}`}>
              <Checkbox
                key={`${name}-${item.label}`}
                label={item.label}
                checked={isChecked}
                onChange={() => handleNewSelection(item)}
                {...itemProps}
                className={styles['checkbox-label']}
                sizing="fill"
                aria-selected={isChecked}
              />
            </li>
          )
        })}
      </ul>
    </div>
  )
}
