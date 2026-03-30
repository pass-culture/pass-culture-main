import { CollectiveOffersSortingColumn } from '@/commons/core/OfferEducational/types'
import { SortOrder } from '@/commons/hooks/useColumnSorting'

const sortByDate = (dateA: string, dateB: string, order: SortOrder) => {
  return (
    (dateA === dateB ? 0 : dateA > dateB ? -1 : 1) *
    (order === SortOrder.ASC ? -1 : 1)
  )
}

export function sortCollectiveOffers<
  T extends { dates?: { start?: string; end?: string } | null },
>(
  offers: T[],
  currentSortingColumn: CollectiveOffersSortingColumn | null,
  sortingMode: SortOrder | null
) {
  const sortedOffers = offers.slice()

  if (currentSortingColumn === CollectiveOffersSortingColumn.EVENT_DATE && sortingMode) {
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
