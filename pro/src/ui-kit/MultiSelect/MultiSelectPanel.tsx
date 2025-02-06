import { useMemo, useState } from 'react'

import strokeSearch from 'icons/stroke-search.svg'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'

import { Option, Options } from './MultiSelect'
import styles from './MultiSelect.module.scss'

type MultiSelectPanelProps = {
  id: string
  className?: string
  label: string
  mergedOptions: (Option & { checked: boolean })[]
  options: Options[]
  hasSelectAllOptions?: boolean
  isAllChecked: boolean
  hasSearch?: boolean
  searchLabel?: string
  onOptionSelect: (option: Option) => void
  onSelectAllOptions: (option: Option[], index?: number) => void
  checkboxStates: Record<number, boolean>
}

export const MultiSelectPanel = ({
  id,
  mergedOptions,
  options,
  onOptionSelect,
  onSelectAllOptions,
  checkboxStates,
  hasSearch = false,
  searchLabel,
  hasSelectAllOptions,
  isAllChecked,
}: MultiSelectPanelProps): JSX.Element => {
  const [searchValue, setSearchValue] = useState('')

  const filteredOptions = useMemo(
    () =>
      mergedOptions.filter((option) =>
        option.label.toLowerCase().includes(searchValue.toLowerCase())
      ),
    [mergedOptions, searchValue]
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

      <div className={styles['panel-scrollable']} data-testid="panel-scrollable">
        <p className={styles['visually-hidden']} role="status">
          <span>{filteredOptions.length} résultats trouvés</span>
        </p>
        {filteredOptions.length > 0 ? (
          <ul className={styles['container']}>
            {hasSelectAllOptions && (
              <li key={'all-options'} className={styles.item}>
                <BaseCheckbox
                  label={'Tout sélectionner'}
                  checked={isAllChecked}
                  labelClassName={styles['label']}
                  inputClassName={styles['checkbox']}
                  onChange={() => onSelectAllOptions(mergedOptions)}
                />
              </li>
            )}
            {options.map((elm, index) => elm.hasSelectAllOptions && (
              <li key={'all-other-options'} className={styles.item}>
                <BaseCheckbox
                  label={elm.selectAllLabel}
                  checked={checkboxStates[index]}
                  labelClassName={styles['label']}
                  inputClassName={styles['checkbox']}
                  onChange={() => onSelectAllOptions(elm.options, index)}
                />
              </li>
            ))}
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
