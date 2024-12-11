import { useMemo, useState } from 'react'

import strokeSearch from 'icons/stroke-search.svg'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'

import { Option } from './MultiSelect'
import styles from './MultiSelect.module.scss'

type MultiSelectPanelPropsBase = {
  className?: string
  label: string
  options: (Option & { checked: boolean })[]
  onOptionSelect: (option: Option) => void
}

type MultiSelectPanelProps = MultiSelectPanelPropsBase &
  (
    | {
        hasSearch: true
        searchExample: string
      }
    | {
        hasSearch?: false
        searchExample: never
      }
  )

export const MultiSelectPanel = ({
  className,
  label,
  options,
  onOptionSelect,
  hasSearch = true,
  ...props
}: MultiSelectPanelProps): JSX.Element => {
  const [searchValue, setSearchValue] = useState('')
  const searchedValues = useMemo(
    () =>
      options.filter((option) =>
        option.label.toLowerCase().includes(searchValue.toLowerCase())
      ),
    [options, searchValue]
  )

  if (hasSearch) {
    props.searchExample
  }

  props.searchExample

  return (
    <div className={styles['panel']}>
      {hasSearch && (
        <BaseInput
          type="search"
          leftIcon={strokeSearch}
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
        />
      )}

      {searchedValues.length > 0 ? (
        <ul className={styles.container} aria-label="Liste des options">
          {searchedValues.map((option) => (
            <li key={option.id} className={styles.item}>
              <BaseCheckbox
                className={styles.checkbox}
                label={option.label}
                checked={option.checked}
                onChange={() => onOptionSelect(option)}
              />
            </li>
          ))}
        </ul>
      ) : (
        'Aucun résultat pour votre recherche'
      )}
    </div>
  )
}
