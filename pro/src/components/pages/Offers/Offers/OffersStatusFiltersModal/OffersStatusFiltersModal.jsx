import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useRef } from 'react'

import { RadioInput } from 'components/layout/inputs/RadioInput/RadioInput'
import { ALL_STATUS } from 'components/pages/Offers/Offers/_constants'

export const OffersStatusFiltersModal = ({
  isVisible,
  applyFilters,
  status,
  setIsVisible,
  updateStatusFilter,
}) => {
  const modalRef = useRef(null)

  const handleStatusFilterChange = useCallback(
    event => {
      updateStatusFilter(event.target.value)
    },
    [updateStatusFilter]
  )

  const onClickOutside = useCallback(
    event => {
      const { target } = event
      if (modalRef.current && !modalRef.current.contains(target)) {
        event.preventDefault()
        event.stopPropagation()

        setIsVisible(!isVisible)
      }
    },
    [setIsVisible, isVisible]
  )

  useEffect(() => {
    document.body.addEventListener('click', onClickOutside)

    return () => {
      document.body.removeEventListener('click', onClickOutside)
    }
  }, [onClickOutside])

  if (!isVisible) {
    return null
  }

  return (
    <div className="offers-status-filters" ref={modalRef}>
      <div className="osf-title">Afficher les statuts</div>
      <RadioInput
        checked={status === ALL_STATUS}
        label="Tous"
        name="status"
        onChange={handleStatusFilterChange}
        value={ALL_STATUS}
      />
      <RadioInput
        checked={status === 'ACTIVE'}
        label="Active"
        name="status"
        onChange={handleStatusFilterChange}
        value="ACTIVE"
      />
      <RadioInput
        checked={status === 'INACTIVE'}
        label="Inactive"
        name="status"
        onChange={handleStatusFilterChange}
        value="INACTIVE"
      />
      <RadioInput
        checked={status === 'SOLD_OUT'}
        label="Épuisée"
        name="status"
        onChange={handleStatusFilterChange}
        value="SOLD_OUT"
      />
      <RadioInput
        checked={status === 'EXPIRED'}
        label="Expirée"
        name="status"
        onChange={handleStatusFilterChange}
        value="EXPIRED"
      />
      <RadioInput
        checked={status === 'PENDING'}
        label="Validation en attente"
        name="status"
        onChange={handleStatusFilterChange}
        value="PENDING"
      />
      <RadioInput
        checked={status === 'REJECTED'}
        label="Refusée"
        name="status"
        onChange={handleStatusFilterChange}
        value="REJECTED"
      />
      <button className="primary-button" onClick={applyFilters} type="button">
        Appliquer
      </button>
    </div>
  )
}

OffersStatusFiltersModal.defaultProps = {
  status: null,
}

OffersStatusFiltersModal.propTypes = {
  applyFilters: PropTypes.func.isRequired,
  isVisible: PropTypes.bool.isRequired,
  setIsVisible: PropTypes.func.isRequired,
  status: PropTypes.string,
  updateStatusFilter: PropTypes.func.isRequired,
}
