import React, { Fragment, useState } from 'react'

import { OfferStatus } from 'apiClient/v1'
import { CollectiveOfferStatus } from 'core/OfferEducational'
import {
  ADMINS_DISABLED_FILTERS_MESSAGE,
  OFFER_STATUS_LIST,
} from 'core/Offers/constants'
import { Audience } from 'core/shared'
import Icon from 'ui-kit/Icon/Icon'

import { OffersStatusFiltersModal } from '../OffersStatusFiltersModal/OffersStatusFiltersModal'

type StatusFiltersButtonProps = {
  applyFilters: () => void
  disabled?: boolean
  status?: OfferStatus | CollectiveOfferStatus | 'all'
  updateStatusFilter: (
    status: OfferStatus | CollectiveOfferStatus | 'all'
  ) => void
  audience: Audience
}

const StatusFiltersButton = ({
  disabled = false,
  applyFilters,
  status,
  updateStatusFilter,
  audience,
}: StatusFiltersButtonProps) => {
  const [isStatusFiltersVisible, setIsStatusFiltersVisible] = useState(false)

  const isFilteredByStatus = Boolean(
    status && OFFER_STATUS_LIST.some(s => s === status)
  )

  function toggleStatusFiltersVisibility() {
    setIsStatusFiltersVisible(!isStatusFiltersVisible)
  }

  return (
    <Fragment>
      <button
        disabled={disabled}
        onClick={toggleStatusFiltersVisibility}
        title={disabled ? ADMINS_DISABLED_FILTERS_MESSAGE : undefined}
        type="button"
      >
        Statut
        <Icon
          alt="Afficher ou masquer le filtre par statut"
          className={isFilteredByStatus ? 'active-status-filter' : undefined}
          svg={
            isFilteredByStatus
              ? 'ico-filter-status-active'
              : 'ico-filter-status-red'
          }
        />
      </button>
      <OffersStatusFiltersModal
        applyFilters={applyFilters}
        isVisible={isStatusFiltersVisible}
        setIsVisible={setIsStatusFiltersVisible}
        status={status}
        updateStatusFilter={updateStatusFilter}
        audience={audience}
      />
    </Fragment>
  )
}

export default StatusFiltersButton
