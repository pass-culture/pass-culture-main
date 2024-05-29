import cn from 'classnames'
import React, { Fragment, useState } from 'react'

import { OfferStatus } from 'apiClient/v1'
import { CollectiveOfferStatus } from 'core/OfferEducational/types'
import {
  ADMINS_DISABLED_FILTERS_MESSAGE,
  ALL_STATUS,
} from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { Audience } from 'core/shared/types'
import fullSortIcon from 'icons/full-sort.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { OffersStatusFiltersModal } from '../OffersStatusFiltersModal/OffersStatusFiltersModal'

import styles from './StatusFiltersButton.module.scss'

export const collectiveFilterStatus = [
  { label: 'Toutes', value: ALL_STATUS },
  { label: 'Désactivée', value: CollectiveOfferStatus.INACTIVE },
  { label: 'Expirée', value: CollectiveOfferStatus.EXPIRED },
  { label: 'Préréservée', value: CollectiveOfferStatus.PREBOOKED },
  { label: 'Publiée sur ADAGE', value: CollectiveOfferStatus.ACTIVE },
  {
    label: 'Refusée',
    value: CollectiveOfferStatus.REJECTED,
  },
  {
    label: 'Réservée',
    value: CollectiveOfferStatus.BOOKED,
  },
  { label: 'Terminée', value: CollectiveOfferStatus.ENDED },
  {
    label: 'Validation en attente',
    value: CollectiveOfferStatus.PENDING,
  },
]

export const individualFilterStatus = [
  { label: 'Toutes', value: ALL_STATUS },
  { label: 'Brouillon', value: OfferStatus.DRAFT },
  { label: 'Publiée', value: OfferStatus.ACTIVE },
  { label: 'Désactivée', value: OfferStatus.INACTIVE },
  { label: 'Épuisée', value: OfferStatus.SOLD_OUT },
  { label: 'Expirée', value: OfferStatus.EXPIRED },
  { label: 'Validation en attente', value: OfferStatus.PENDING },
  { label: 'Refusée', value: OfferStatus.REJECTED },
]

export type StatusFiltersButtonProps = {
  applyFilters: () => void
  disabled?: boolean
  status?: SearchFiltersParams['status']
  updateStatusFilter: (status: SearchFiltersParams['status']) => void
  audience: Audience
}

export const StatusFiltersButton = ({
  disabled = false,
  applyFilters,
  status,
  updateStatusFilter,
  audience,
}: StatusFiltersButtonProps) => {
  const [isStatusFiltersVisible, setIsStatusFiltersVisible] = useState(false)

  const isFilteredByStatus = Boolean(status && status !== ALL_STATUS)

  function toggleStatusFiltersVisibility() {
    setIsStatusFiltersVisible(!isStatusFiltersVisible)
  }

  const filters =
    audience === Audience.INDIVIDUAL
      ? individualFilterStatus
      : collectiveFilterStatus

  return (
    <Fragment>
      <button
        disabled={disabled}
        onClick={toggleStatusFiltersVisibility}
        title={disabled ? ADMINS_DISABLED_FILTERS_MESSAGE : undefined}
        type="button"
        aria-expanded={isStatusFiltersVisible}
        aria-controls="offer-status-filters-modal"
      >
        Statut
        {isFilteredByStatus && (
          <span className="visually-hidden">
            Tri par statut {filters.find((x) => x.value === status)?.label}{' '}
            actif
          </span>
        )}
        <span className={styles['status-container']}>
          <SvgIcon
            alt="Afficher ou masquer le filtre par statut"
            src={fullSortIcon}
            className={cn(
              styles['status-icon'],
              (isFilteredByStatus || isStatusFiltersVisible) &&
                styles['status-icon-active']
            )}
          />
          {isFilteredByStatus && (
            <span className={styles['status-badge-icon']} />
          )}
        </span>
      </button>
      {isStatusFiltersVisible && (
        <OffersStatusFiltersModal
          applyFilters={applyFilters}
          setIsVisible={setIsStatusFiltersVisible}
          status={status}
          updateStatusFilter={updateStatusFilter}
          audience={audience}
        />
      )}
    </Fragment>
  )
}
