import { useCallback, useEffect } from 'react'
import { useSearchParams } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { getV2FinanceInvoicesData } from '@/apiClient/v1'
import {
  GET_HAS_INVOICE_QUERY_KEY,
  GET_INVOICES_QUERY_KEY,
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { BannerReimbursementsInfo } from './BannerReimbursementsInfo'
import { DEFAULT_INVOICES_FILTERS } from './constants'
import { InvoicesFilters } from './InvoicesFilters'
import { InvoicesServerError } from './InvoicesServerError'
import { InvoiceTable } from './InvoiceTable/InvoiceTable'

function extractFilters(
  urlParams: URLSearchParams
): getV2FinanceInvoicesData['query'] {
  const amountPositiveOnly = urlParams.get('amountPositiveOnly')
  const amountNegativeOnly = urlParams.get('amountNegativeOnly')
  return {
    periodBeginningDate:
      urlParams.get('periodBeginningDate') ??
      DEFAULT_INVOICES_FILTERS.periodBeginningDate,
    periodEndingDate:
      urlParams.get('periodEndingDate') ??
      DEFAULT_INVOICES_FILTERS.periodEndingDate,
    ...(amountNegativeOnly && {
      amountNegativeOnly: amountNegativeOnly === 'true',
    }),
    ...(amountPositiveOnly && {
      amountPositiveOnly: amountPositiveOnly === 'true',
    }),
  }
}

const ReimbursementsInvoices = (): JSX.Element => {
  const [searchParams, setSearchParams] = useSearchParams()
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const isCaledonian = selectedAdminOfferer.isCaledonian
  const snackBar = useSnackBar()

  const offererId = selectedAdminOfferer?.id

  useEffect(() => {
    if (searchParams.size === 0) {
      setSearchParams(DEFAULT_INVOICES_FILTERS)
    }
  }, [searchParams, setSearchParams])

  const hasInvoiceQuery = useSWR(
    offererId ? [GET_HAS_INVOICE_QUERY_KEY, offererId] : null,
    ([, offererId]) => api.hasInvoice({ query: { offererId: offererId } }),
    { fallbackData: { hasInvoice: false } }
  )

  const hasInvoice = Boolean(hasInvoiceQuery.data?.hasInvoice)

  const getInvoicesQuery = useSWR(
    offererId && hasInvoice
      ? [GET_INVOICES_QUERY_KEY, offererId, searchParams]
      : null,
    async () => {
      const invoices = await api.getInvoicesV2({
        query: {
          offererId: offererId,
          ...extractFilters(searchParams),
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
      api.getOffererBankAccountsAndAttachedVenues({
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

  const handleResetFilters = useCallback(() => {
    setSearchParams(DEFAULT_INVOICES_FILTERS)
  }, [setSearchParams])

  if (
    getOffererBankAccountsAndAttachedVenuesQuery.isLoading ||
    getInvoicesQuery.isLoading ||
    hasInvoiceQuery.isLoading
  ) {
    return <Spinner />
  }

  const bankAccounts =
    getOffererBankAccountsAndAttachedVenuesQuery.data?.bankAccounts ?? []

  const invoices = getInvoicesQuery.data ?? []

  return (
    <>
      <BannerReimbursementsInfo />
      <InvoicesFilters onReset={handleResetFilters} />
      {getInvoicesQuery.error ? (
        <InvoicesServerError />
      ) : (
        <InvoiceTable
          data={invoices}
          hasInvoice={hasInvoice}
          hasBankAccount={bankAccounts.length > 0}
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
