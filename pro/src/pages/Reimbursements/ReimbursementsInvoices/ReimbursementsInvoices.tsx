import { format, subMonths } from 'date-fns'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  GET_HAS_INVOICE_QUERY_KEY,
  GET_INVOICES_QUERY_KEY,
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { FORMAT_ISO_DATE_ONLY, getToday } from '@/commons/utils/date'
import { isEqual } from '@/commons/utils/isEqual'
import { sortByLabel } from '@/commons/utils/strings'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { DEFAULT_INVOICES_FILTERS } from '../_constants'
import { BannerReimbursementsInfo } from './BannerReimbursementsInfo'
import { InvoicesFilters } from './InvoicesFilters'
import { InvoicesServerError } from './InvoicesServerError'
import { InvoiceTable } from './InvoiceTable/InvoiceTable'

export const ReimbursementsInvoices = (): JSX.Element => {
  const [, setSearchParams] = useSearchParams()
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const adminSelectedOfferer = useAppSelector(
    (store) => store.offerer.adminCurrentOfferer
  )
  const isCaledonian = useIsCaledonian(withSwitchVenueFeature)

  const offererId = withSwitchVenueFeature
    ? adminSelectedOfferer?.id
    : selectedOffererId

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

  useEffect(() => {
    const newParams = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      newParams.set(key, value)
    })
    setSearchParams(newParams, { replace: true })
  }, [filters, setSearchParams])

  const hasInvoiceQuery = useSWR(
    offererId ? [GET_HAS_INVOICE_QUERY_KEY, offererId] : null,
    ([, offererId]) => api.hasInvoice(offererId),
    { fallbackData: { hasInvoice: false } }
  )

  const hasInvoice = Boolean(hasInvoiceQuery.data.hasInvoice)

  const getInvoicesQuery = useSWR(
    offererId && hasInvoice
      ? [GET_INVOICES_QUERY_KEY, offererId, searchFilters]
      : null,
    async () => {
      const { periodStart, periodEnd, reimbursementPoint } = searchFilters
      const invoices = await api.getInvoicesV2(
        periodStart,
        periodEnd,
        reimbursementPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
          ? parseInt(reimbursementPoint, 10)
          : undefined,
        offererId
      )

      return invoices
    },
    {
      fallbackData: [],
    }
  )

  const getOffererBankAccountsAndAttachedVenuesQuery = useSWR(
    offererId
      ? [GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY, offererId]
      : null,
    ([, selectedOffererId]) =>
      api.getOffererBankAccountsAndAttachedVenues(selectedOffererId)
  )

  const handleSearch = useCallback(() => {
    setSearchFilters(filters)
  }, [filters])

  const handleResetFilters = useCallback(() => {
    setFilters(INITIAL_FILTERS)
    setSearchFilters(INITIAL_FILTERS)
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

  const invoices = getInvoicesQuery.data

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
      {getInvoicesQuery.error ? (
        <InvoicesServerError />
      ) : (
        <InvoiceTable
          data={invoices}
          hasInvoice={hasInvoice}
          isLoading={getInvoicesQuery.isLoading}
          isCaledonian={isCaledonian}
          onFilterReset={handleResetFilters}
        />
      )}
    </>
  )
}
