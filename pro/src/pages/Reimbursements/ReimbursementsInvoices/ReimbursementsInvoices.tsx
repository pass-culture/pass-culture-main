import { format, subMonths } from 'date-fns'
import { useEffect, useMemo, useState } from 'react'
import { useSelector } from 'react-redux'
import { useSearchParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  GET_HAS_INVOICE_QUERY_KEY,
  GET_INVOICES_QUERY_KEY,
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'commons/utils/date'
import { sortByLabel } from 'commons/utils/strings'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { DEFAULT_INVOICES_FILTERS } from '../_constants'

import { BannerReimbursementsInfo } from './BannerReimbursementsInfo'
import { InvoicesFilters } from './InvoicesFilters'
import { InvoicesNoResult } from './InvoicesNoResult'
import { InvoicesServerError } from './InvoicesServerError'
import { InvoiceTable } from './InvoiceTable/InvoiceTable'
import { NoInvoicesYet } from './NoInvoicesYet'

export const ReimbursementsInvoices = (): JSX.Element => {
  const [searchParams, setSearchParams] = useSearchParams()

  const INITIAL_FILTERS = useMemo(() => {
    const today = getToday()
    const oneMonthAgo = subMonths(today, 1)
    return {
      reimbursementPoint: DEFAULT_INVOICES_FILTERS.reimbursementPointId,
      periodStart: format(oneMonthAgo, FORMAT_ISO_DATE_ONLY),
      periodEnd: format(today, FORMAT_ISO_DATE_ONLY),
    }
  }, [])

  const [filters, setFilters] = useState(INITIAL_FILTERS)

  useEffect(() => {
    const { reimbursementPoint, periodStart, periodEnd } = filters
    searchParams.set('reimbursementPoint', reimbursementPoint)
    searchParams.set('periodStart', periodStart)
    searchParams.set('periodEnd', periodEnd)
    setSearchParams(searchParams, { replace: true })

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, setSearchParams])

  const [areFiltersDefault, setAreFiltersDefault] = useState(true)
  const [hasSearchedOnce, setHasSearchedOnce] = useState(false)
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const getInvoicesQuery = useSWR(
    selectedOffererId
      ? [GET_INVOICES_QUERY_KEY, selectedOffererId, searchParams.toString()]
      : null,
    async () => {
      const reimbursmentPoint = filters.reimbursementPoint
      const periodStart = filters.periodStart
      const periodEnd = filters.periodEnd

      const invoices = await api.getInvoicesV2(
        periodStart,
        periodEnd,
        reimbursmentPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
          ? parseInt(reimbursmentPoint)
          : undefined,
        selectedOffererId
      )

      return invoices
    },
    { fallbackData: [] }
  )

  const hasInvoiceQuery = useSWR(
    selectedOffererId ? [GET_HAS_INVOICE_QUERY_KEY, selectedOffererId] : null,
    ([, selectedOffererId]) => api.hasInvoice(selectedOffererId),
    { fallbackData: { hasInvoice: false } }
  )

  const getOffererBankAccountsAndAttachedVenuesQuery = useSWR(
    selectedOffererId
      ? [
          GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
          selectedOffererId,
        ]
      : null,
    ([, selectedOffererId]) =>
      api.getOffererBankAccountsAndAttachedVenues(selectedOffererId)
  )

  if (
    getOffererBankAccountsAndAttachedVenuesQuery.isLoading ||
    getInvoicesQuery.isLoading ||
    hasInvoiceQuery.isLoading
  ) {
    return <Spinner />
  }

  const bankAccounts =
    getOffererBankAccountsAndAttachedVenuesQuery.data?.bankAccounts ?? []

  const filterOptions = sortByLabel(
    bankAccounts.map((item) => ({
      value: String(item.id),
      label: item.label,
    }))
  )
  const invoices = getInvoicesQuery.data

  const hasInvoice = Boolean(hasInvoiceQuery.data.hasInvoice)

  const hasNoSearchResult =
    (!getInvoicesQuery.error && !invoices.length && hasSearchedOnce) ||
    (!invoices.length && hasInvoice)

  const hasNoInvoicesYet = !hasSearchedOnce && !hasInvoice

  return (
    <>
      <BannerReimbursementsInfo />
      <InvoicesFilters
        areFiltersDefault={areFiltersDefault}
        filters={filters}
        initialFilters={INITIAL_FILTERS}
        selectableOptions={filterOptions}
        setAreFiltersDefault={setAreFiltersDefault}
        setFilters={setFilters}
        setHasSearchedOnce={setHasSearchedOnce}
      />
      {getInvoicesQuery.error && <InvoicesServerError />}
      {hasNoInvoicesYet && <NoInvoicesYet />}
      {hasNoSearchResult && !getInvoicesQuery.error && (
        <InvoicesNoResult
          areFiltersDefault={areFiltersDefault}
          initialFilters={INITIAL_FILTERS}
          setAreFiltersDefault={setAreFiltersDefault}
          setFilters={setFilters}
        />
      )}
      {invoices.length > 0 && <InvoiceTable invoices={invoices} />}
    </>
  )
}
