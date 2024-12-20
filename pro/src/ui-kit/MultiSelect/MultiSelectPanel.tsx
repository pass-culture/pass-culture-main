import { useMemo, useState } from 'react'

import strokeSearch from 'icons/stroke-search.svg'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'

import { Option } from './MultiSelect'
import styles from './MultiSelect.module.scss'

type MultiSelectPanelProps = {
  className?: string
  label: string
  options: (Option & { checked: boolean })[]
  onOptionSelect: (option: Option | 'all' | undefined) => void
  hasSearch?: boolean
  searchExample?: string
  searchLabel?: string
  hasSelectAllOptions?: boolean
}

export const MultiSelectPanel = ({
  options,
  onOptionSelect,
  hasSearch = false,
  searchExample,
  searchLabel,
  hasSelectAllOptions,
}: MultiSelectPanelProps): JSX.Element => {
  const [searchValue, setSearchValue] = useState('')
  const [isSelectAllChecked, setIsSelectAllChecked] = useState(false)
  const searchedValues = useMemo(
    () =>
      options.filter((option) =>
        option.label.toLowerCase().includes(searchValue.toLowerCase())
      ),
    [options, searchValue]
  )

  const onToggleAllOptions = (checked: boolean) => {
    if (checked) {
      onOptionSelect(undefined)
    } else {
      onOptionSelect('all')
    }
    setIsSelectAllChecked(!checked)
  }

  const onToggleOption = (option: Option, checked: boolean) => {
    if (checked) {
      setIsSelectAllChecked(false)
    }
    onOptionSelect(option)
  }

  return (
    <div className={styles['panel']}>
      {hasSearch && (
        <>
          <label className={styles['visually-hidden']} htmlFor="search-input">
            {searchLabel}
          </label>
          <BaseInput
            type="search"
            id="search-input"
            leftIcon={strokeSearch}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
          />
          <span className={styles['search-example']}>{searchExample}</span>
        </>
      )}

      {searchedValues.length > 0 ? (
        <ul className={styles['container']} aria-label="Liste des options">
          {hasSelectAllOptions && (
            <li key={'all-options'} className={styles['item']}>
              <BaseCheckbox
                label={'Tout sélectionner'}
                checked={isSelectAllChecked}
                onChange={() => onToggleAllOptions(isSelectAllChecked)}
              />
              <div className={styles['separator']} />
            </li>
          )}
          {searchedValues.map((option) => (
            <li key={option.id} className={styles.item}>
              <BaseCheckbox
                className={styles['checkbox']}
                label={option.label}
                checked={option.checked}
                onChange={() => onToggleOption(option, option.checked)}
              />
            </li>
          ))}
        </ul>
      ) : (
        <span>{'Aucun résultat trouvé pour votre recherche.'}</span>
      )}
    </div>
  )
}
