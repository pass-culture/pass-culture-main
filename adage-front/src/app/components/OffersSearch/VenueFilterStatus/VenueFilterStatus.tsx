import './VenueFilterStatus.scss'

import React from 'react'

import { VenueFilterType } from 'utils/types'

import { ReactComponent as CloseIcon } from './assets/close.svg'

export const VenueFilterStatus = ({
  removeFilter,
  venueFilter,
}: {
  removeFilter: () => void
  venueFilter: VenueFilterType
}): JSX.Element => (
  <div className="venue-filter">
    <span className="filter-label">Lieu filtré :</span>
    <div className="venue-label">
      <span className="venue-label-text">
        {venueFilter.publicName || venueFilter.name}
      </span>
      <button onClick={removeFilter} type="button">
        <CloseIcon />
      </button>
    </div>
  </div>
)
