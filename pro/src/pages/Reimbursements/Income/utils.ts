import type { CollectiveRevenue, TotalRevenue } from '@/apiClient/v1'

export const isCollectiveAndIndividualRevenue = (
  revenue: Partial<TotalRevenue> | undefined
): revenue is TotalRevenue => {
  return (
    revenue?.collective !== undefined &&
    revenue?.individual !== undefined &&
    revenue?.total !== undefined
  )
}

export const isCollectiveRevenue = (
  revenue: Partial<TotalRevenue> | undefined
): revenue is CollectiveRevenue => {
  return (
    revenue?.collective !== undefined &&
    revenue?.individual === undefined &&
    revenue?.total === undefined
  )
}
