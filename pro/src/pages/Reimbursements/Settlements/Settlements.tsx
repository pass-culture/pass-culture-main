import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  GET_HAS_SETTLEMENT_QUERY_KEY,
  GET_SETTLEMENTS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { SettlementTable } from './components/SettlementTable/SettlementTable'

export const Settlements = (): JSX.Element => {
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const offererId = selectedAdminOfferer?.id

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
  if (isLoading || hasSettlementQuery.isLoading) {
    return <Spinner />
  }

  return (
    <SettlementTable
      settlements={settlements}
      isLoading={isLoading}
      hasSettlement={hasSettlement}
      // TODO(mdesquilbet, 19/08/2026): make the call to actually know about bankaccounts
      hasBankAccount={true}
    />
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Settlements
