import { useCallback, useEffect } from 'react'
import { useSearchParams } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { getFinanceSettlementsData } from '@/apiClient/v1'
import {
  GET_HAS_SETTLEMENT_QUERY_KEY,
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
  GET_SETTLEMENTS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { DEFAULT_INVOICES_FILTERS } from '../ReimbursementsInvoices/constants'
import { SettlementsFilters } from './components/SettlementsFilters/SettlementsFilters'
import { SettlementTable } from './components/SettlementTable/SettlementTable'

function extractFilters(
  urlParams: URLSearchParams
): Omit<getFinanceSettlementsData['query'], 'offererId'> {
  const bankAccountId = urlParams.get('bankAccountId')
  const nameSearch = urlParams.get('nameSearch')
  return {
    periodBeginningDate:
      urlParams.get('periodBeginningDate') ??
      DEFAULT_INVOICES_FILTERS.periodBeginningDate,
    periodEndingDate:
      urlParams.get('periodEndingDate') ??
      DEFAULT_INVOICES_FILTERS.periodEndingDate,
    ...(bankAccountId && { bankAccountId: Number(bankAccountId) }),
    ...(nameSearch && { nameSearch }),
  }
}

export const Settlements = (): JSX.Element => {
  const [searchParams, setSearchParams] = useSearchParams()
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const snackBar = useSnackBar()
  const offererId = selectedAdminOfferer?.id

  useEffect(() => {
    if (searchParams.size === 0) {
      setSearchParams(DEFAULT_INVOICES_FILTERS)
    }
  }, [searchParams, setSearchParams])

  const handleResetFilters = useCallback(() => {
    setSearchParams(DEFAULT_INVOICES_FILTERS)
  }, [setSearchParams])

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

  const hasSettlementQuery = useSWR(
    offererId ? [GET_HAS_SETTLEMENT_QUERY_KEY, offererId] : null,
    ([, offererId]) => api.hasSettlement({ query: { offererId: offererId } }),
    { fallbackData: { hasSettlement: false } }
  )

  const hasSettlement = Boolean(hasSettlementQuery.data?.hasSettlement)

  const { isLoading, data: settlements } = useSWR(
    offererId && hasSettlement
      ? [GET_SETTLEMENTS_QUERY_KEY, offererId, searchParams]
      : null,
    async () => {
      const settlements = await api.getSettlements({
        query: { offererId, ...extractFilters(searchParams) },
      })
      return settlements
    },
    {
      fallbackData: [],
    }
  )
  if (
    getOffererBankAccountsAndAttachedVenuesQuery.isLoading ||
    hasSettlementQuery.isLoading ||
    isLoading
  ) {
    return <Spinner />
  }

  const bankAccounts =
    getOffererBankAccountsAndAttachedVenuesQuery.data?.bankAccounts ?? []

  return (
    <>
      <SettlementsFilters
        bankAccounts={bankAccounts}
        onReset={handleResetFilters}
      />

      <SettlementTable
        settlements={settlements}
        isLoading={isLoading}
        hasSettlement={hasSettlement}
        hasBankAccount={bankAccounts.length > 0}
        onFilterReset={handleResetFilters}
      />
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Settlements
