import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  GET_HAS_SETTLEMENT_QUERY_KEY,
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
  GET_SETTLEMENTS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { SettlementTable } from './components/SettlementTable/SettlementTable'

export const Settlements = (): JSX.Element => {
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const snackBar = useSnackBar()
  const offererId = selectedAdminOfferer?.id

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
    offererId && hasSettlement ? [GET_SETTLEMENTS_QUERY_KEY, offererId] : null,
    async () => {
      const settlements = await api.getSettlements({
        query: { offererId: offererId },
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
    <SettlementTable
      settlements={settlements}
      isLoading={isLoading}
      hasSettlement={hasSettlement}
      hasBankAccount={bankAccounts.length > 0}
    />
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Settlements
