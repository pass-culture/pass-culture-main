import { CollectiveOfferResponseModel } from '@/apiClient//v1'
import { CollectiveOffersSortingColumn } from '@/commons/core/OfferEducational/types'
import { SortingMode } from '@/commons/hooks/useColumnSorting'

const sortByDate = (dateA: string, dateB: string, mode: SortingMode) => {
  return (
    (dateA === dateB ? 0 : dateA > dateB ? -1 : 1) *
    (mode === SortingMode.ASC ? -1 : 1)
  )
}

export function sortCollectiveOffers(
  offers: CollectiveOfferResponseModel[],
  currentSortingColumn: CollectiveOffersSortingColumn | null,
  sortingMode: SortingMode
) {
  const sortedOffers = offers.slice()

  if (currentSortingColumn === CollectiveOffersSortingColumn.EVENT_DATE) {
    return sortedOffers.sort((offerA, offerB) =>
      sortByDate(
        offerA.dates?.start ?? '',
        offerB.dates?.start ?? '',
        sortingMode
      )
    )
  }
  return sortedOffers
}
