import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import Icon from 'components/layout/Icon'

import { OFFER_STATUS_LIST } from './_constants'
import { OffersStatusFiltersModal } from './OffersStatusFiltersModal/OffersStatusFiltersModal'

const StatusFiltersButton = ({
  refreshOffers,
  status,
  updateStatusFilter,
  isStatusFiltersVisible,
  setIsStatusFiltersVisible,
}) => {
  const isFilteredByStatus = OFFER_STATUS_LIST.includes(status)
  function toggleStatusFiltersVisibility() {
    setIsStatusFiltersVisible(!isStatusFiltersVisible)
  }

  return (
    <Fragment>
      <button
        onClick={toggleStatusFiltersVisibility}
        type="button"
      >
        {'Statut'}
        <Icon
          alt="Afficher ou masquer le filtre par statut"
          className={isFilteredByStatus ? 'active-status-filter' : undefined}
          svg={isFilteredByStatus ? 'ico-filter-status-active' : 'ico-filter-status-red'}
        />
      </button>
      <OffersStatusFiltersModal
        isVisible={isStatusFiltersVisible}
        refreshOffers={refreshOffers}
        setIsVisible={setIsStatusFiltersVisible}
        status={status}
        updateStatusFilter={updateStatusFilter}
      />
    </Fragment>
  )
}

export default StatusFiltersButton

StatusFiltersButton.defaultProps = {
  isStatusFiltersVisible: false,
  status: null,
}

StatusFiltersButton.propTypes = {
  isStatusFiltersVisible: PropTypes.bool,
  refreshOffers: PropTypes.func.isRequired,
  setIsStatusFiltersVisible: PropTypes.func.isRequired,
  status: PropTypes.string,
  updateStatusFilter: PropTypes.func.isRequired,
}
