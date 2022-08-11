import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import { InvoiceResponseModel } from 'apiClient/v1'
import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'
import { getToday } from 'utils/date'

import InvoicesAdminMustFilter from './InvoicesAdminMustFilter'
import InvoicesFilters from './InvoicesFilters'
import InvoicesNoResult from './InvoicesNoResult'
import InvoicesServerError from './InvoicesServerError'
import { InvoiceTable } from './InvoiceTable'
import NoInvoicesYet from './NoInvoicesYet'

interface IReimbursementsInvoicesProps {
  isCurrentUserAdmin: boolean
  reimbursementPointsOptions: SelectOptionsRFF
}

const ReimbursementsInvoices = ({
  isCurrentUserAdmin,
  reimbursementPointsOptions,
}: IReimbursementsInvoicesProps): JSX.Element => {
  const ALL_REIMBURSEMENT_POINT_OPTION_ID = 'all'

  const INITIAL_FILTERS = useMemo(() => {
    const today = getToday()
    const oneMonthAgo = new Date(
      today.getFullYear(),
      today.getMonth() - 1,
      today.getDate()
    )
    return {
      reimbursementPoint: ALL_REIMBURSEMENT_POINT_OPTION_ID,
      businessUnit: ALL_REIMBURSEMENT_POINT_OPTION_ID,
      periodStart: oneMonthAgo,
      periodEnd: today,
    }
  }, [])

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const [invoices, setInvoices] = useState<InvoiceResponseModel[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [areFiltersDefault, setAreFiltersDefault] = useState(true)
  const [hasSearchedOnce, setHasSearchedOnce] = useState(false)
  const isCalledOnceRef = useRef(false)

  const {
    reimbursementPoint: selectedReimbursementPoint,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  const isPeriodFilterSelected = selectedPeriodStart && selectedPeriodEnd
  const requireBUFilterForAdmin =
    isCurrentUserAdmin &&
    selectedReimbursementPoint === ALL_REIMBURSEMENT_POINT_OPTION_ID

  const hasNoSearchResult =
    !hasError && invoices.length === 0 && hasSearchedOnce

  const shouldDisplayAdminInfo =
    !hasError && isCurrentUserAdmin && !hasSearchedOnce

  const hasNoInvoicesYetForNonAdmin =
    !hasError &&
    !isCurrentUserAdmin &&
    invoices.length === 0 &&
    !hasSearchedOnce

  const shouldDisableButton =
    !isPeriodFilterSelected ||
    requireBUFilterForAdmin ||
    hasNoInvoicesYetForNonAdmin

  const loadInvoices = useCallback(
    (shouldReset?: boolean) => {
      if (shouldReset) {
        setHasSearchedOnce(false)
      }
      const invoicesFilters = {
        reimbursementPointId: filters.reimbursementPoint,
        businessUnitId: filters.reimbursementPoint,
        periodBeginningDate: filters.periodStart,
        periodEndingDate: filters.periodEnd,
      }
      pcapi
        .getInvoices(shouldReset ? INITIAL_FILTERS : invoicesFilters)
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
    [
      INITIAL_FILTERS,
      filters.reimbursementPoint,
      filters.periodEnd,
      filters.periodStart,
    ]
  )

  useEffect(() => {
    if (!isCalledOnceRef.current) {
      isCalledOnceRef.current = true
      loadInvoices()
    }
  }, [loadInvoices])

  return (
    <>
      <InvoicesFilters
        areFiltersDefault={areFiltersDefault}
        filters={filters}
        disable={hasNoInvoicesYetForNonAdmin}
        initialFilters={INITIAL_FILTERS}
        loadInvoices={loadInvoices}
        selectableOptions={reimbursementPointsOptions}
        setAreFiltersDefault={setAreFiltersDefault}
        setFilters={setFilters}
      >
        <button
          className="primary-button search-button"
          disabled={shouldDisableButton}
          onClick={() => {
            setHasSearchedOnce(true)
            loadInvoices()
          }}
          type="button"
        >
          Lancer la recherche
        </button>
      </InvoicesFilters>
      {isLoading && <Spinner />}
      {hasError && <InvoicesServerError />}
      {hasNoInvoicesYetForNonAdmin && <NoInvoicesYet />}
      {hasNoSearchResult && (
        <InvoicesNoResult
          areFiltersDefault={areFiltersDefault}
          initialFilters={INITIAL_FILTERS}
          loadInvoices={loadInvoices}
          setAreFiltersDefault={setAreFiltersDefault}
          setFilters={setFilters}
        />
      )}
      {shouldDisplayAdminInfo && <InvoicesAdminMustFilter />}
      {invoices.length > 0 && <InvoiceTable invoices={invoices} />}
    </>
  )
}

export default ReimbursementsInvoices
