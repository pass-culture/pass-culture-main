import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'

/**
 * Build the link to the offer details page :
 *
 * @param offerId The offer id
 * @param displayedStatus The offer displayedStatus
 * @param isEditionMode If we should return the edition link (only for non draft offers)
 */
export function getCollectiveOfferLink(
  offerId: number | string,
  displayedStatus: CollectiveOfferDisplayedStatus,
  isEditionMode: boolean = false
): string {
  if (displayedStatus === CollectiveOfferDisplayedStatus.DRAFT) {
    return `/offre/collectif/${offerId}/creation`
  }

  if (isEditionMode) {
    return `/offre/${offerId}/collectif/edition`
  }

  return `/offre/${offerId}/collectif/recapitulatif`
}
