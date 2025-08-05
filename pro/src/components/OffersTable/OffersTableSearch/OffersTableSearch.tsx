import cn from 'classnames'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import {
  FilterConfigType,
  getStoredFilterConfig,
  useStoredFilterConfig,
} from 'components/OffersTable/OffersTableSearch/utils'
import fullRefreshIcon from 'icons/full-refresh.svg'
import { useState } from 'react'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { ButtonFilter } from 'ui-kit/ButtonFilter/ButtonFilter'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from './OffersTableSearch.module.scss'

export type OffersTableSearchProps = {
  type: FilterConfigType
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void
  isDisabled: boolean
  hasActiveFilters: boolean
  nameInputProps: {
    label: JSX.Element | string
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
  const isStoreAndToggleFiltersEnabled = useActiveFeature(
    'WIP_COLLAPSED_MEMORIZED_FILTERS'
  )
  const [filtersVisibility, setFiltersVisibility] = useState(
    isStoreAndToggleFiltersEnabled
      ? getStoredFilterConfig(type).filtersVisibility
      : true
  )

  const toggleFiltersVisibility = () => {
    const newFiltersVisibility = !filtersVisibility

    onFiltersToggle(newFiltersVisibility)
    setFiltersVisibility(newFiltersVisibility)
  }

  return (
    <form onSubmit={onSubmit} className={styles['offers-table-search']}>
      <div className={styles['offers-table-search-name-and-toggle-row']}>
        <FieldLayout
          className={styles['offers-table-search-input-wrapper']}
          label={nameInputProps.label}
          name="offre"
          isOptional
        >
          <BaseInput
            type="search"
            disabled={nameInputProps.disabled}
            name="offre"
            onChange={nameInputProps.onChange}
            value={nameInputProps.value}
          />
        </FieldLayout>
        {isStoreAndToggleFiltersEnabled && (
          <ButtonFilter
            className={styles['offers-table-search-toggle-button']}
            isActive={hasActiveFilters}
            isOpen={filtersVisibility}
            onClick={toggleFiltersVisibility}
            aria-controls="offers-filter"
            aria-expanded={filtersVisibility}
          >
            Filtrer
            {hasActiveFilters && (
              <span className={styles['visually-hidden']}>actifs</span>
            )}
          </ButtonFilter>
        )}
      </div>
      <div
        id="offers-filter"
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
