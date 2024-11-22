import { CollectiveAndIndividualRevenue, CollectiveRevenue } from 'apiClient/v1'

export const isCollectiveAndIndividualRevenue = (revenue: any): revenue is CollectiveAndIndividualRevenue => {
  return (
    revenue?.collective !== undefined
    && revenue?.individual !== undefined
    && revenue?.total !== undefined
  )
}

export const isCollectiveRevenue = (revenue: any): revenue is CollectiveRevenue => {
  return (
    revenue?.collective !== undefined
    && revenue?.individual === undefined
    && revenue?.total === undefined
  )
}
