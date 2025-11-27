import cn from 'classnames'
import { useId, useState } from 'react'

import {
  type FilterConfigType,
  getStoredFilterConfig,
  useStoredFilterConfig,
} from '@/components/OffersTableSearch/utils'
import { SearchInput } from '@/design-system/SearchInput/SearchInput'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { ButtonFilter } from '@/ui-kit/ButtonFilter/ButtonFilter'

import styles from './OffersTableSearch.module.scss'

export type OffersTableSearchProps = {
  type: FilterConfigType
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void
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
  searchButtonRef?: React.RefObject<HTMLButtonElement>
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
  const [filtersVisibility, setFiltersVisibility] = useState(
    getStoredFilterConfig(type).filtersVisibility
  )

  const toggleFiltersVisibility = () => {
    const newFiltersVisibility = !filtersVisibility

    onFiltersToggle(newFiltersVisibility)
    setFiltersVisibility(newFiltersVisibility)
  }

  const searchId = useId()

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
          isOpen={filtersVisibility}
          onClick={toggleFiltersVisibility}
          aria-controls={`offers-filter-${searchId}`}
          aria-expanded={filtersVisibility}
        >
          Filtrer
          {hasActiveFilters && (
            // TODO (igabriele, 2025-11-27): Check "Filtrer actifs" wording + accessibility.
            <span className={styles['visually-hidden']}>actifs</span>
          )}
        </ButtonFilter>
      </div>
      <div
        id={`offers-filter-${searchId}`}
        data-testid="offers-filter"
        className={cn(styles['offers-table-search-filters'], {
          [styles['offers-table-search-filters-collapsed']]: !filtersVisibility,
        })}
      >
        {children}
        <div className={styles['offers-table-search-reset-wrapper']}>
          <Button
            icon={fullRefreshIcon}
            disabled={!hasActiveFilters}
            onClick={onResetFilters}
            variant={ButtonVariant.TERNARY}
            className={styles['offers-table-search-reset-button']}
          >
            Réinitialiser les filtres
          </Button>
        </div>
      </div>
      <div className={styles['offers-table-search-separator-wrapper']}>
        <div className={styles['offers-table-search-separator-element']} />
        <Button type="submit" disabled={isDisabled} ref={searchButtonRef}>
          Rechercher
        </Button>
        <div className={styles['offers-table-search-separator-element']} />
      </div>
    </form>
  )
}
