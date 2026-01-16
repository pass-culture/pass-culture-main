import { useMemo, useState } from 'react'

import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { SearchInput } from '@/design-system/SearchInput/SearchInput'

import type { Option } from './MultiSelect'
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

  function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Escape' && searchValue) {
      //  In case the search input is in a dropdown or in a modal
      event.stopPropagation()
    }
  }

  return (
    <div id={id} className={styles['panel']}>
      {hasSearch && (
        <div className={styles['search-input']}>
          <SearchInput
            name="search"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            label={searchLabel || 'Rechercher'}
            onKeyDown={handleKeyDown}
          />
        </div>
      )}

      <div
        className={styles['panel-scrollable']}
        data-testid="panel-scrollable"
      >
        {/** biome-ignore lint/a11y/useSemanticElements: We want a `role="status"` here, not an `<output />`. */}
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
                  sizing="fill"
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
                  sizing="fill"
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
