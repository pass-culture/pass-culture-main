import React, { useState } from 'react'

import { getToday } from 'utils/date'

import ReimbursementsTable from '../../../new_components/Table'

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
  invoices: []
  columns: [
    {
      title: string
      sortBy: string
      selfDirection: string
    }
  ]
}

const ReimbursementsProofs = ({
  isCurrentUserAdmin,
  venuesOptions,
  invoices,
  columns,
}: IReimbursementsProofsProps): JSX.Element => {
  const ALL_VENUES_OPTION_ID = 'allVenues'
  const today = getToday()
  const oneMonthAgo = new Date(
    today.getFullYear(),
    today.getMonth() - 1,
    today.getDate()
  )
  const INITIAL_FILTERS = {
    venue: ALL_VENUES_OPTION_ID,
    periodStart: oneMonthAgo,
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
          Lancer la recherche
        </button>
      </ReimbursementsSectionHeader>
      <ReimbursementsTable columns={columns} invoices={invoices} />
    </>
  )
}

export default ReimbursementsProofs
