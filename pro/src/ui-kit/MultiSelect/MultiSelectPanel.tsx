import { useMemo, useState } from 'react'

import strokeSearch from 'icons/stroke-search.svg'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
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

      <div className={styles['panel-scrollable']}>
        <p className={styles['visually-hidden']} role="status">
          <span>{filteredOptions.length} résultats trouvés</span>
        </p>
        {filteredOptions.length > 0 ? (
          <ul className={styles['container']} aria-label="Liste des options">
            {hasSelectAllOptions && (
              <li key={'all-options'} className={styles.item}>
                <BaseCheckbox
                  label={'Tout sélectionner'}
                  checked={isAllChecked}
                  labelClassName={styles['label']}
                  inputClassName={styles['checkbox']}
                  onChange={onSelectAll}
                />
              </li>
            )}
            {filteredOptions.map((option) => (
              <li key={option.id} className={styles.item}>
                <BaseCheckbox
                  labelClassName={styles['label']}
                  inputClassName={styles['checkbox']}
                  label={option.label}
                  checked={option.checked}
                  onChange={() => onOptionSelect(option)}
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
