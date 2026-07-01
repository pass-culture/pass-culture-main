import type { CollectiveAdditionalFeeModel } from '@/apiClient/v1'

export function computePriceForStock(
  servicePrice: number | null,
  additionalFees: CollectiveAdditionalFeeModel[]
): number {
  return additionalFees.reduce(
    (total, fee) => total + fee.amount,
    servicePrice || 0
  )
}
