import { useCombobox } from 'downshift'
import { useField, useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

import { BaseInput } from '../shared/BaseInput/BaseInput'

import styles from './AdageMultiselect.module.scss'

interface ItemProps {
  label: string
  value: number | string | string[]
}

interface AdageMultiselectProps {
  options: ItemProps[]
  placeholder: string
  name: string
  label: string
  isOpen: boolean
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
  placeholder,
  name,
  label,
  isOpen,
  sortOptions,
  filterMaxLength = 255,
}: AdageMultiselectProps) => {
  // We need to maintain the input value in state so that we can use it in itemToString
  const [inputValue, setInputValue] = useState('')
  const [field] = useField<ItemProps['value'][]>(name)
  const { setFieldValue } = useFormikContext<any>()
  const [sortedOptions, setSortedOptions] = useState<ItemProps[]>([])

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
      switch (type) {
        case useCombobox.stateChangeTypes.InputKeyDownEnter:
        case useCombobox.stateChangeTypes.ItemClick:
          return {
            ...changes,
            // We force isOpen to true because we always want to display the list of options
            isOpen: true,
          }
        default:
          return changes
      }
    },
    onInputValueChange: ({ inputValue: newInputValue }) => {
      setInputValue(newInputValue || '')
    },
    // By default downshift will use this callback to display the selected item, we just want to always display the input value
    itemToString: () => inputValue,
  })

  const handleNewSelection = async (selection: ItemProps) => {
    if (isIncluded(field.value, selection.value)) {
      if (field.value.length > 0 && Array.isArray(field.value[0])) {
        await setFieldValue(
          name,
          (field.value as string[][]).filter(
            (item) =>
              !(selection.value as string[]).some((el) => item.includes(el))
          )
        )
        return
      }
      await setFieldValue(
        name,
        field.value.filter((item) => !isIncluded([selection.value], item))
      )
    } else {
      await setFieldValue(name, [...field.value, selection.value])
    }
  }

  // The isOpen modal state is handle outside of the component, we want to clear the input and sort items on open/close
  useEffect(() => {
    setInputValue('')
    setDownshiftInputValue('')
    setSortedOptions((sortOptions ?? defaultSortOptions)(options, field.value))
  }, [isOpen])

  return (
    <div className={styles['container']}>
      <label htmlFor="search" className="visually-hidden" {...getLabelProps()}>
        {label}
      </label>
      <BaseInput
        type="search"
        name="search"
        className={styles['search-input']}
        placeholder={placeholder}
        maxLength={filterMaxLength}
        value={inputValue}
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
          const { ref, ...itemProps } = getItemProps({ item, index })
          const liValueKey = Array.isArray(item.value)
            ? item.value.join('_')
            : item.value

          const isChecked = isIncluded(field.value, item.value)

          return (
            <li key={`${liValueKey}`}>
              <BaseCheckbox
                key={`${name}-${item.label}`}
                label={item.label}
                name={name}
                checked={isChecked}
                onChange={() => handleNewSelection(item)}
                {...itemProps}
                aria-selected={isChecked}
              />
            </li>
          )
        })}
      </ul>
    </div>
  )
}
