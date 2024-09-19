import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { SortingMode } from 'hooks/useColumnSorting'
import { CollectiveOffersSortingColumn } from 'screens/CollectiveOffersScreen/CollectiveOffersScreen'

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

  switch (currentSortingColumn) {
    case CollectiveOffersSortingColumn.EVENT_DATE:
      return sortedOffers.sort((offerA, offerB) =>
        sortByDate(
          offerA.dates?.start ?? '',
          offerB.dates?.start ?? '',
          sortingMode
        )
      )
    default:
      return sortedOffers
  }
}
