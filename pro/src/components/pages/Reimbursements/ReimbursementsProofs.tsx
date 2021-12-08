import React, { useState } from 'react'

import { getToday } from 'utils/date'
import ReimbursementsSectionHeader from './ReimbursementsSectionHeader'

type venuesOptionsType = [
  {
    id: string
    displayName: string
  }
]

interface IReimbursementsProofsProps {
  isCurrentUserAdmin: boolean
  venuesOptions: venuesOptionsType
}

const ReimbursementsProofs = ({
  isCurrentUserAdmin,
  venuesOptions,
}: IReimbursementsProofsProps): JSX.Element => {
  const ALL_VENUES_OPTION_ID = 'allVenues'
  const today = getToday()
  const oneYearAgo = new Date(
    today.getFullYear() - 1,
    today.getMonth(),
    today.getDate()
  )
  const INITIAL_FILTERS = {
    venue: ALL_VENUES_OPTION_ID,
    periodStart: oneYearAgo,
    periodEnd: today,
  }

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const {
    venue: selectedVenue,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  const isPeriodFilterSelected = selectedPeriodStart && selectedPeriodEnd
  const requireVenueFilterForAdmin =
    isCurrentUserAdmin && selectedVenue === 'allVenues'
  const shouldDisableButton =
    !isPeriodFilterSelected || requireVenueFilterForAdmin

  return (
    <>
      <ReimbursementsSectionHeader
        filters={filters}
        headerTitle="Affichage des justificatifs de remboursement"
        initialFilters={INITIAL_FILTERS}
        setFilters={setFilters}
        venuesOptions={venuesOptions}
      >
        <button
          className="primary-button"
          disabled={shouldDisableButton}
          type="button"
        >
          Afficher
        </button>
      </ReimbursementsSectionHeader>
      <div> TABLEAU </div>
    </>
  )
}

export default ReimbursementsProofs
