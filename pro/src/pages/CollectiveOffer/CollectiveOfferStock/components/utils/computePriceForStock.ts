import type { CollectiveAdditionalFeeModel } from '@/apiClient/v1'

export function computePriceForStock(
  servicePrice: number | null,
  collectiveAdditionnalFees: CollectiveAdditionalFeeModel[]
): number {
  return collectiveAdditionnalFees.reduce(
    (total, fee) => total + (fee.amount || 0),
    servicePrice || 0
  )
}
