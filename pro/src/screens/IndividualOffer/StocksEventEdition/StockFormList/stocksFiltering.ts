import { PriceCategoryResponseModel } from 'apiClient/v1'
import { sortStockByPriceCategory } from 'components/StocksEventList/stocksFiltering'
import {
  SortingMode,
  sortColumnByDateString,
  sortColumnByNumber,
} from 'hooks/useColumnSorting'
import { isDateValid } from 'utils/date'

import { StockEventFormValues } from './types'

export enum StocksEventFormSortingColumn {
  DATE = 'DATE',
  HOUR = 'HOUR',
  PRICE_CATEGORY = 'PRICE_CATEGORY',
  BOOKING_LIMIT_DATETIME = 'BOOKING_LIMIT_DATETIME',
  REMAINING_QUANTITY = 'REMAINING_QUANTITY',
  BOOKINGS_QUANTITY = 'BOOKINGS_QUANTITY',
}

export const filterAndSortStocks = (
  stocks: StockEventFormValues[],
  priceCategories: PriceCategoryResponseModel[],
  sortingColumn: StocksEventFormSortingColumn | null,
  sortingMode: SortingMode,
  filters: {
    dateFilter: string
    hourFilter: string
    priceCategoryFilter: string
  }
): StockEventFormValues[] => {
  const { dateFilter, hourFilter, priceCategoryFilter } = filters
  const filteredStocks = stocks.filter(stock => {
    const stockDate = new Date(stock.beginningDate)

    const date = new Date(dateFilter)
    if (isDateValid(date) && isDateValid(stockDate)) {
      const isSameDay =
        stockDate.getFullYear() === date.getFullYear() &&
        stockDate.getMonth() === date.getMonth() &&
        stockDate.getDate() === date.getDate()

      if (!isSameDay) {
        return false
      }
    }

    const [stockHours, stockMinutes] = stock.beginningTime.split(':')
    const [filterHours, filterMinutes] = hourFilter.split(':')
    if (filterHours && filterMinutes) {
      const isSameHour =
        stockHours === filterHours && stockMinutes === filterMinutes

      if (!isSameHour) {
        return false
      }
    }

    if (
      priceCategoryFilter !== '' &&
      stock.priceCategoryId !== priceCategoryFilter
    ) {
      return false
    }

    return true
  })

  if (sortingMode === SortingMode.NONE || sortingColumn === null) {
    return sortColumnByDateString(
      filteredStocks,
      'beginningDate',
      SortingMode.ASC
    )
  }

  switch (sortingColumn) {
    case StocksEventFormSortingColumn.DATE:
      return sortColumnByDateString(
        filteredStocks,
        'beginningDate',
        sortingMode
      )
    case StocksEventFormSortingColumn.HOUR:
      return sortColumnByDateString(
        filteredStocks,
        'beginningTime',
        sortingMode
      )
    case StocksEventFormSortingColumn.PRICE_CATEGORY:
      return sortStockByPriceCategory(
        filteredStocks,
        priceCategories,
        sortingMode
      )
    case StocksEventFormSortingColumn.BOOKING_LIMIT_DATETIME:
      return sortColumnByDateString(
        filteredStocks,
        'bookingLimitDatetime',
        sortingMode
      )
    case StocksEventFormSortingColumn.BOOKINGS_QUANTITY:
      return sortColumnByNumber(filteredStocks, 'bookingsQuantity', sortingMode)
    case StocksEventFormSortingColumn.REMAINING_QUANTITY:
      return sortColumnByNumber(
        filteredStocks,
        'remainingQuantity',
        sortingMode
      )

    default:
      throw new Error('Unknown sorting column')
  }
}
