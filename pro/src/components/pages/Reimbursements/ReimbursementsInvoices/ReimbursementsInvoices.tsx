import React, { useCallback, useEffect, useRef, useState } from 'react'

import * as pcapi from 'repository/pcapi/pcapi'
import { getToday } from 'utils/date'

import Spinner from '../../../layout/Spinner'
import ReimbursementsTable from '../ReimbursementsTable'

import InvoicesFilters from './InvoicesFilters'

type businessUnitsOptionsType = [
  {
    id: string
    displayName: string
  }
]

interface IReimbursementsInvoicesProps {
  isCurrentUserAdmin: boolean
  businessUnitsOptions: businessUnitsOptionsType
}

const ReimbursementsInvoices = ({
  isCurrentUserAdmin,
  businessUnitsOptions,
}: IReimbursementsInvoicesProps): JSX.Element => {
  const columns = [
    {
      title: 'Date',
      sortBy: 'date',
      selfDirection: 'default',
    },
    {
      title: 'Point de remboursement',
      sortBy: 'businessUnit',
      selfDirection: 'default',
    },
    {
      title: 'Référence',
      sortBy: 'reference',
      selfDirection: 'default',
    },
    {
      title: 'Montant remboursé',
      sortBy: 'amount',
      selfDirection: 'default',
    },
  ]

  const ALL_BUSINESS_UNITS_OPTION_ID = 'all'
  const today = getToday()
  const oneMonthAgo = new Date(
    today.getFullYear(),
    today.getMonth() - 1,
    today.getDate()
  )
  const INITIAL_FILTERS = {
    businessUnit: ALL_BUSINESS_UNITS_OPTION_ID,
    periodStart: oneMonthAgo,
    periodEnd: today,
  }

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const [invoices, setInvoices] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const isCalledOnceRef = useRef(false)

  const {
    businessUnit: selectedBusinessUnit,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  const isPeriodFilterSelected = selectedPeriodStart && selectedPeriodEnd
  const requireVenueFilterForAdmin =
    isCurrentUserAdmin && selectedBusinessUnit === ALL_BUSINESS_UNITS_OPTION_ID
  const shouldDisableButton =
    !isPeriodFilterSelected || requireVenueFilterForAdmin

  const loadInvoices = useCallback(() => {
    const invoicesFilters = {
      businessUnitId: filters.businessUnit,
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
  }, [filters.businessUnit, filters.periodEnd, filters.periodStart])

  useEffect(() => {
    if (!isCalledOnceRef.current) {
      isCalledOnceRef.current = true
      loadInvoices()
    }
  }, [loadInvoices])

  return (
    <>
      <InvoicesFilters
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
          onClick={() => loadInvoices()}
          type="button"
        >
          Lancer la recherche
        </button>
      </InvoicesFilters>
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
