import cn from 'classnames'
import { useState } from 'react'

import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { FilterConfigType, getStoredFilterConfig, useStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'
import fullRefreshIcon from 'icons/full-refresh.svg'
import strokeDownIcon from 'icons/stroke-down.svg'
import strokeUpIcon from 'icons/stroke-up.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
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
}

export const OffersTableSearch = ({
  type,
  onSubmit,
  isDisabled,
  hasActiveFilters,
  nameInputProps,
  onResetFilters,
  children,
}: OffersTableSearchProps) => {
  const { onFiltersToggle } = useStoredFilterConfig(type)
  const isStoreAndToggleFiltersEnabled = useActiveFeature('WIP_COLLAPSED_MEMORIZED_FILTERS')
  const [filtersVisibility, setFiltersVisibility] = useState(
    isStoreAndToggleFiltersEnabled ?
      getStoredFilterConfig(type).filtersVisibility :
      true
  )

  const toggleFiltersVisibility = () => {
    const newFiltersVisibility = !filtersVisibility

    onFiltersToggle(newFiltersVisibility)
    setFiltersVisibility(newFiltersVisibility)
  }

  return (
    <form
      onSubmit={onSubmit}
      className={styles['offers-table-search']}
    >
      <FormLayout.Row
        className={styles['offers-table-search-name-and-toggle-row']}
        inline
      >
        <FieldLayout
          className={styles['offers-table-search-name-input']}
          label={nameInputProps.label}
          name="offre"
          isOptional
          hideFooter
        >
          <BaseInput
            type="text"
            disabled={nameInputProps.disabled}
            name="offre"
            onChange={nameInputProps.onChange}
            value={nameInputProps.value}
          />
        </FieldLayout>
        {isStoreAndToggleFiltersEnabled && (
          <Button
            className={cn(styles['offers-table-search-toggle-button'], {
                [styles['offers-table-search-toggle-button-active']]: hasActiveFilters
              }
            )}
            icon={filtersVisibility ? strokeUpIcon : strokeDownIcon}
            iconPosition={IconPositionEnum.RIGHT}
            variant={ButtonVariant.BOX}
            onClick={toggleFiltersVisibility}
            aria-controls="offers-filter"
            aria-expanded="false"
          >
            Filtres
            {hasActiveFilters && <span className={styles['visually-hidden']}>actifs</span>}
          </Button>
        )}
      </FormLayout.Row>
      <div
        id="offers-filter"
        data-testid="offers-filter"
        className={cn(styles['offers-table-search-filters'], {
          [styles['offers-table-search-filters-collapsed']]: !filtersVisibility
        })}
      >
        <FormLayout.Row inline className={styles['offers-table-search-filters-row']}>
          {children}
        </FormLayout.Row>
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
        <Button type="submit" disabled={isDisabled}>
          Rechercher
        </Button>
        <div className={styles['offers-table-search-separator-element']} />
      </div>
    </form>
  )
}
