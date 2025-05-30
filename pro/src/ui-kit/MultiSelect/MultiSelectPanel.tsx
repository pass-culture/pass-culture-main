import { useMemo, useState } from 'react'

import { Checkbox } from 'design-system/Checkbox/Checkbox'
import strokeSearch from 'icons/stroke-search.svg'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'

import { Option } from './MultiSelect'
import styles from './MultiSelect.module.scss'

type MultiSelectPanelProps = {
  id: string
  className?: string
  label: string
  options: (Option & { checked: boolean })[]
  hasSelectAllOptions?: boolean
  isAllChecked: boolean
  hasSearch?: boolean
  searchLabel?: string
  onOptionSelect: (option: Option) => void
  onSelectAll: () => void
}

export const MultiSelectPanel = ({
  id,
  options,
  onOptionSelect,
  onSelectAll,
  hasSearch = false,
  searchLabel,
  hasSelectAllOptions,
  isAllChecked,
}: MultiSelectPanelProps): JSX.Element => {
  const [searchValue, setSearchValue] = useState('')

  const filteredOptions = useMemo(
    () =>
      options.filter((option) =>
        option.label.toLowerCase().includes(searchValue.toLowerCase())
      ),
    [options, searchValue]
  )

  return (
    <div id={id} className={styles['panel']}>
      {hasSearch && (
        <div className={styles['search-input']}>
          <label
            className={styles['visually-hidden']}
            htmlFor={`search-input-${id}`}
          >
            {searchLabel}
          </label>
          <BaseInput
            type="search"
            id={`search-input-${id}`}
            leftIcon={strokeSearch}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            autoComplete="off"
            spellCheck={false}
          />
        </div>
      )}

      <div
        className={styles['panel-scrollable']}
        data-testid="panel-scrollable"
      >
        <p className={styles['visually-hidden']} role="status">
          <span>{filteredOptions.length} résultats trouvés</span>
        </p>
        {filteredOptions.length > 0 ? (
          <ul className={styles['container']}>
            {hasSelectAllOptions && (
              <li key={'all-options'} className={styles.item}>
                <Checkbox
                  label={'Tout sélectionner'}
                  checked={isAllChecked}
                  className={styles['label']}
                  onChange={onSelectAll}
                  display="fill"
                />
              </li>
            )}
            {filteredOptions.map((option) => (
              <li key={option.id} className={styles.item}>
                <Checkbox
                  className={styles['label']}
                  label={option.label}
                  checked={option.checked}
                  onChange={() => onOptionSelect(option)}
                  display="fill"
                />
              </li>
            ))}
          </ul>
        ) : (
          <div className={styles['empty-search']}>
            <span>{'Aucun résultat trouvé pour votre recherche.'}</span>
          </div>
        )}
      </div>
    </div>
  )
}
