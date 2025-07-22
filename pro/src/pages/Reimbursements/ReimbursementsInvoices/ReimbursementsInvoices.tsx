import { format, subMonths } from 'date-fns'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSelector } from 'react-redux'
import { useSearchParams } from 'react-router'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  GET_HAS_INVOICE_QUERY_KEY,
  GET_INVOICES_QUERY_KEY,
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'commons/utils/date'
import { isEqual } from 'commons/utils/isEqual'
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
  const [, setSearchParams] = useSearchParams()
  const selectedOffererId = useSelector(selectCurrentOffererId)

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
  const [searchFilters, setSearchFilters] = useState(INITIAL_FILTERS)
  const [hasSearchedOnce, setHasSearchedOnce] = useState(false)

  useEffect(() => {
    const newParams = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      newParams.set(key, value)
    })
    setSearchParams(newParams, { replace: true })
  }, [filters, setSearchParams])

  const getInvoicesQuery = useSWR(
    selectedOffererId
      ? [GET_INVOICES_QUERY_KEY, selectedOffererId, searchFilters]
      : null,
    async () => {
      const { periodStart, periodEnd, reimbursementPoint } = searchFilters
      const invoices = await api.getInvoicesV2(
        periodStart,
        periodEnd,
        reimbursementPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
          ? parseInt(reimbursementPoint)
          : undefined,
        selectedOffererId
      )

      return invoices
    },
    {
      fallbackData: [],
    }
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

  const handleSearch = useCallback(() => {
    setHasSearchedOnce(true)
    setSearchFilters(filters)
  }, [filters])

  const handleResetFilters = useCallback(() => {
    setFilters(INITIAL_FILTERS)
    setSearchFilters(INITIAL_FILTERS)
    setHasSearchedOnce(false)
  }, [INITIAL_FILTERS])

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

  const invoices = [
    {
      reference: 'INV-001',
      date: '2024-06-01',
      amount: 150,
      bankAccountLabel: 'Bank A',
      cashflowLabels: ['VIRE-001'],
      url: '',
    },
    {
      reference: 'INV-002',
      date: '2024-05-15',
      amount: -50,
      bankAccountLabel: 'Bank B',
      cashflowLabels: ['VIRE-002'],
      url: '',
    },
    {
      reference: 'INV-003',
      date: '2024-05-15',
      amount: -50,
      bankAccountLabel: 'Bank B',
      cashflowLabels: ['VIRE-002'],
      url: '',
    },
    {
      reference: 'INV-004',
      date: '2024-05-15',
      amount: -50,
      bankAccountLabel: 'Bank B',
      cashflowLabels: ['VIRE-002'],
      url: '',
    },
  ]

  const hasInvoice = Boolean(hasInvoiceQuery.data.hasInvoice)
  const hasNoSearchResult =
    (!getInvoicesQuery.error && !invoices.length && hasSearchedOnce) ||
    (!invoices.length && hasInvoice)
  const hasNoInvoicesYet = !hasSearchedOnce && !hasInvoice

  return (
    <>
      <BannerReimbursementsInfo />
      <InvoicesFilters
        areFiltersDefault={isEqual(filters, INITIAL_FILTERS)}
        filters={filters}
        selectableOptions={filterOptions}
        setFilters={setFilters}
        onReset={handleResetFilters}
        onSearch={handleSearch}
      />
      {getInvoicesQuery.error && <InvoicesServerError />}
      {hasNoInvoicesYet && <NoInvoicesYet />}
      {hasNoSearchResult && !getInvoicesQuery.error && (
        <InvoicesNoResult
          areFiltersDefault={isEqual(filters, INITIAL_FILTERS)}
          onReset={handleResetFilters}
        />
      )}
      {invoices.length > 0 && <InvoiceTable invoices={invoices} />}
    </>
  )
}
