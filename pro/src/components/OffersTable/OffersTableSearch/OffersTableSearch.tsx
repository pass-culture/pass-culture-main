import cn from 'classnames'
import { useState } from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import fullRefreshIcon from 'icons/full-refresh.svg'
import strokeDownIcon from 'icons/stroke-down.svg'
import strokeUpIcon from 'icons/stroke-up.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from './OffersTableSearch.module.scss'

export type OffersTableSearchProps = {
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void
  filtersVisibility: boolean
  onFiltersToggle: () => void
  isDisabled: boolean
  nameInputProps: {
    label: JSX.Element | string
    disabled: boolean
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
    value: string
  }
  resetButtonProps: {
    onClick: () => void
    isDisabled: boolean
  }
  children: React.ReactNode
}

export const OffersTableSearch = ({
  onSubmit,
  filtersVisibility,
  onFiltersToggle,
  isDisabled,
  nameInputProps,
  resetButtonProps,
  children,
}: OffersTableSearchProps) => {
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
        <Button
          className={styles['offers-table-search-toggle-button']}
          icon={filtersVisibility ? strokeUpIcon : strokeDownIcon}
          iconPosition={IconPositionEnum.RIGHT}
          variant={ButtonVariant.BOX}
          onClick={onFiltersToggle}
          aria-controls="offers-filter"
          aria-expanded="false"
        >
          Filtres
        </Button>
      </FormLayout.Row>
      <div
        id="offers-filter"
        data-testid="offers-filter"
        className={cn(styles['offers-table-search-filters'], {
          [styles['offers-table-search-filters-collapsed']]: !filtersVisibility
        })}
      >
        {children}
        <div className={styles['offers-table-search-reset-wrapper']}>
          <Button
            icon={fullRefreshIcon}
            disabled={resetButtonProps.isDisabled}
            onClick={resetButtonProps.onClick}
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
