import { format, subMonths } from 'date-fns'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router'
import useSWR from 'swr'

import { apiNew } from '@/apiClient/api'
import {
  GET_HAS_INVOICE_QUERY_KEY,
  GET_INVOICES_QUERY_KEY,
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { FORMAT_ISO_DATE_ONLY, getToday } from '@/commons/utils/date'
import { isEqual } from '@/commons/utils/isEqual'
import { sortByLabel } from '@/commons/utils/strings'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { DEFAULT_INVOICES_FILTERS } from '../_constants'
import { BannerReimbursementsInfo } from './BannerReimbursementsInfo'
import { InvoicesFilters } from './InvoicesFilters'
import { InvoicesServerError } from './InvoicesServerError'
import { InvoiceTable } from './InvoiceTable/InvoiceTable'

const ReimbursementsInvoices = (): JSX.Element => {
  const [, setSearchParams] = useSearchParams()
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const isCaledonian = selectedAdminOfferer.isCaledonian
  const snackBar = useSnackBar()

  const offererId = selectedAdminOfferer?.id

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
    ([, offererId]) => apiNew.hasInvoice({ query: { offererId: offererId } }),
    { fallbackData: { hasInvoice: false } }
  )

  const hasInvoice = Boolean(hasInvoiceQuery.data?.hasInvoice)

  const getInvoicesQuery = useSWR(
    offererId && hasInvoice
      ? [GET_INVOICES_QUERY_KEY, offererId, searchFilters]
      : null,
    async () => {
      const { periodStart, periodEnd, reimbursementPoint } = searchFilters
      const invoices = await apiNew.getInvoicesV2({
        query: {
          periodBeginningDate: periodStart,
          periodEndingDate: periodEnd,
          bankAccountId:
            reimbursementPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
              ? Number.parseInt(reimbursementPoint, 10)
              : undefined,
          offererId: offererId,
        },
      })
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
      apiNew.getOffererBankAccountsAndAttachedVenues({
        path: {
          offerer_id: selectedOffererId,
        },
      }),
    {
      onError: () =>
        snackBar.error(
          'Impossible de récupérer les informations relatives à vos comptes bancaires.'
        ),
    }
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

  const invoices = getInvoicesQuery.data ?? []

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

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = ReimbursementsInvoices
