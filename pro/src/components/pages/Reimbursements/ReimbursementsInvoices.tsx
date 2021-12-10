import React, { useCallback, useEffect, useState } from 'react'

import { getToday } from 'utils/date'

import ReimbursementsTable from '../../../new_components/Table'
import * as pcapi from '../../../repository/pcapi/pcapi'
import Spinner from '../../layout/Spinner'

import ReimbursementsSectionHeader from './ReimbursementsSectionHeader'

type businessUnitsOptionsType = [
  {
    id: string
    displayName: string
  }
]

interface IReimbursementsInvoicesProps {
  isCurrentUserAdmin: boolean
  businessUnitsOptions: businessUnitsOptionsType
  columns: [
    {
      title: string
      sortBy: string
      selfDirection: string
    }
  ]
}

const ReimbursementsInvoices = ({
  isCurrentUserAdmin,
  businessUnitsOptions,
  columns,
}: IReimbursementsInvoicesProps): JSX.Element => {
  const ALL_BUSINESS_UNITS_OPTION_ID = 'all'
  const today = getToday()
  const oneMonthAgo = new Date(
    today.getFullYear(),
    today.getMonth() - 1,
    today.getDate()
  )
  const INITIAL_FILTERS = {
    spot: ALL_BUSINESS_UNITS_OPTION_ID,
    periodStart: oneMonthAgo,
    periodEnd: today,
  }

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const [invoices, setInvoices] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)

  const {
    spot: selectedBusinessUnit,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  const isPeriodFilterSelected = selectedPeriodStart && selectedPeriodEnd
  const requireVenueFilterForAdmin =
    isCurrentUserAdmin && selectedBusinessUnit === ALL_BUSINESS_UNITS_OPTION_ID
  const shouldDisableButton =
    !isPeriodFilterSelected || requireVenueFilterForAdmin

  const loadInvoices = useCallback(
    async filters => {
      const invoicesFilters = {
        businessUnitId: filters.spot,
        periodBeginningDate: filters.periodStart,
        periodEndingDate: filters.periodEnd,
      }
      pcapi
        .getInvoices(invoicesFilters)
        .then(invoices => {
          setInvoices(invoices)
          setIsLoading(false)
          setHasError(false)
        })
        .catch(() => {
          setIsLoading(false)
          setHasError(true)
        })
    },
    [setInvoices]
  )

  useEffect(() => {
    loadInvoices(filters)
  }, [filters, loadInvoices])

  return (
    <>
      <ReimbursementsSectionHeader
        defaultSelectDisplayName="Tous les points de remboursement"
        defaultSelectId="all"
        filters={filters}
        headerTitle="Affichage des justificatifs de remboursement"
        initialFilters={INITIAL_FILTERS}
        selectLabel="Point de remboursement"
        selectName="businessUnit"
        selectableOptions={businessUnitsOptions}
        setFilters={setFilters}
      >
        <button
          className="primary-button"
          disabled={shouldDisableButton}
          onClick={() => loadInvoices(filters)}
          type="button"
        >
          Lancer la recherche
        </button>
      </ReimbursementsSectionHeader>
      {isLoading && <Spinner />}
      {hasError && 'Une erreur est survenue, veuillez réessayer plus tard.'}
      {!hasError && invoices.length === 0 && 'Pas de résultats'}
      {invoices.length > 0 && (
        <ReimbursementsTable columns={columns} invoices={invoices} />
      )}
    </>
  )
}

export default ReimbursementsInvoices
