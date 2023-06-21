import cn from 'classnames'
import React, { Fragment, useState } from 'react'

import { OfferStatus } from 'apiClient/v1'
import { CollectiveOfferStatus } from 'core/OfferEducational'
import {
  ADMINS_DISABLED_FILTERS_MESSAGE,
  OFFER_STATUS_LIST,
} from 'core/Offers/constants'
import { Audience } from 'core/shared'
import fullSortIcon from 'icons/full-sort.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

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
        <span className="status-container">
          <SvgIcon
            alt="Afficher ou masquer le filtre par statut"
            src={fullSortIcon}
            className={cn(
              'status-icon',
              (isFilteredByStatus || isStatusFiltersVisible) && 'active'
            )}
          />
          {isFilteredByStatus && <span className="status-badge-icon"></span>}
        </span>
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
