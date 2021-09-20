import "./VenueFilterStatus.scss"

import React from "react"

import { VenueFilterType } from "utils/types"

export const VenueFilterStatus = ({
  venueFilter,
}: {
  venueFilter: VenueFilterType;
}): JSX.Element => (
  <div className="venue-filter">
    <span className="filter-label">
      Lieu filtré :
    </span>
    <span className="venue-label">
      {venueFilter.name}
    </span>
  </div>
)
