import { type SubmitEventHandler, useId, useState } from 'react'

import {
  type FilterConfigType,
  getStoredFilterConfig,
  useStoredFilterConfig,
} from '@/components/OffersTableSearch/utils'
import { Button } from '@/design-system/Button/Button'
import { SearchInput } from '@/design-system/SearchInput/SearchInput'
import { ButtonFilter } from '@/ui-kit/ButtonFilter/ButtonFilter'

import { OffersTableFilterBar } from '../OffersTableFilterBar/OffersTableFilterBar'
import styles from './OffersTableSearch.module.scss'

export type OffersTableSearchProps = {
  type: FilterConfigType
  onSubmit: SubmitEventHandler<HTMLFormElement>
  isDisabled: boolean
  hasActiveFilters: boolean
  nameInputProps: {
    label: string
    disabled: boolean
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
    value: string
  }
  onResetFilters: () => void
  children: React.ReactNode
  searchButtonRef?: React.RefObject<HTMLButtonElement | null>
}

export const OffersTableSearch = ({
  type,
  onSubmit,
  isDisabled,
  hasActiveFilters,
  nameInputProps,
  onResetFilters,
  children,
  searchButtonRef,
}: OffersTableSearchProps) => {
  const { onFiltersToggle } = useStoredFilterConfig(type)
  const [isExpanded, setIsExpanded] = useState(
    getStoredFilterConfig(type).filtersVisibility
  )

  const toggleFiltersVisibility = () => {
    const willBeExpanded = !isExpanded

    onFiltersToggle(willBeExpanded)
    setIsExpanded(willBeExpanded)
  }

  const collapseableFilterBarId = useId()

  return (
    <form onSubmit={onSubmit} className={styles['offers-table-search']}>
      <div className={styles['offers-table-search-name-and-toggle-row']}>
        <div className={styles['offers-table-search-input-wrapper']}>
          <SearchInput
            label={nameInputProps.label}
            disabled={nameInputProps.disabled}
            onChange={nameInputProps.onChange}
            value={nameInputProps.value}
            name="nameOrIsbn"
          />
        </div>
        <ButtonFilter
          className={styles['offers-table-search-toggle-button']}
          isActive={hasActiveFilters}
          isOpen={isExpanded}
          onClick={toggleFiltersVisibility}
          aria-controls={collapseableFilterBarId}
          aria-expanded={isExpanded}
        >
          Filtrer
          {hasActiveFilters && (
            // TODO (igabriele, 2025-11-27): Check "Filtrer actifs" wording + accessibility.
            <span className={styles['visually-hidden']}>actifs</span>
          )}
        </ButtonFilter>
      </div>
      <OffersTableFilterBar
        id={collapseableFilterBarId}
        isDisabled={!hasActiveFilters}
        isHidden={!isExpanded}
        onReset={onResetFilters}
      >
        {children}
      </OffersTableFilterBar>

      <div className={styles['offers-table-search-separator-wrapper']}>
        <div className={styles['offers-table-search-separator-element']} />
        <Button
          type="submit"
          disabled={isDisabled}
          ref={searchButtonRef}
          label="Rechercher"
        />
        <div className={styles['offers-table-search-separator-element']} />
      </div>
    </form>
  )
}
