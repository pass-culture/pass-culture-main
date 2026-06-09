import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1/new'

import type { CollectiveOfferBookable } from '../types'

export function canExpire(offer: Partial<CollectiveOfferBookable>): boolean {
  return (
    offer.displayedStatus === CollectiveOfferDisplayedStatus.PREBOOKED ||
    offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED
  )
}
