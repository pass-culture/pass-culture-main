import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import { api } from 'apiClient/api'
import { InvoiceResponseModel } from 'apiClient/v1'
import Spinner from 'ui-kit/Spinner/Spinner'
import {
  formatBrowserTimezonedDateAsUTC,
  FORMAT_ISO_DATE_ONLY,
  getToday,
} from 'utils/date'

import { DEFAULT_INVOICES_FILTERS } from '../_constants'

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
      periodStart: oneMonthAgo,
      periodEnd: today,
    }
  }, [])

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const [invoices, setInvoices] = useState<InvoiceResponseModel[]>([])
  const [noInvoices, setNoInvoices] = useState<boolean>(false)
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
    !hasError && invoices.length === 0 && (hasSearchedOnce || !noInvoices)

  const shouldDisplayAdminInfo =
    !hasError && isCurrentUserAdmin && !hasSearchedOnce

  const hasNoInvoicesYetForNonAdmin =
    !hasError &&
    !isCurrentUserAdmin &&
    invoices.length === 0 &&
    noInvoices &&
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
      const reimbursmentPoint = shouldReset
        ? INITIAL_FILTERS.reimbursementPoint
        : filters.reimbursementPoint
      const periodStart = shouldReset
        ? INITIAL_FILTERS.periodStart
        : filters.periodStart
      const periodEnd = shouldReset
        ? INITIAL_FILTERS.periodEnd
        : filters.periodEnd

      api
        .getInvoices(
          periodStart !== DEFAULT_INVOICES_FILTERS.periodBeginningDate
            ? formatBrowserTimezonedDateAsUTC(periodStart, FORMAT_ISO_DATE_ONLY)
            : undefined,
          periodEnd !== DEFAULT_INVOICES_FILTERS.periodEndingDate
            ? formatBrowserTimezonedDateAsUTC(periodEnd, FORMAT_ISO_DATE_ONLY)
            : undefined,
          // @ts-expect-error type string is not assignable to type number
          reimbursmentPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
            ? reimbursmentPoint
            : undefined
        )
        .then(invoices => {
          setInvoices(invoices)
          setIsLoading(false)
          setHasError(false)
          // FIXME: api route getInvoices() should give use this information: does user have at least one invoice in database ?
          setNoInvoices(false)
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
