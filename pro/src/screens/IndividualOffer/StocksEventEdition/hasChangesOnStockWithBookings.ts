import { StockEventFormValues } from './StockFormList/types'

export const hasChangesOnStockWithBookings = (
  submittedStocks: StockEventFormValues[],
  initialStocks: StockEventFormValues[]
) => {
  const initialStocksById: Record<
    string,
    Partial<StockEventFormValues>
  > = initialStocks.reduce(
    (dict: Record<string, Partial<StockEventFormValues>>, stock) => {
      dict[stock.stockId] = {
        priceCategoryId: stock.priceCategoryId,
        beginningDate: stock.beginningDate,
        beginningTime: stock.beginningTime,
      }
      return dict
    },
    {}
  )

  return submittedStocks.some((stock) => {
    if (!stock.bookingsQuantity || stock.bookingsQuantity === 0) {
      return false
    }
    const initialStock = initialStocksById[stock.stockId]
    const fieldsWithWarning: (keyof StockEventFormValues)[] = [
      'priceCategoryId',
      'beginningDate',
      'beginningTime',
    ]

    return fieldsWithWarning.some(
      (fieldName: keyof StockEventFormValues) =>
        initialStock && initialStock[fieldName] !== stock[fieldName]
    )
  })
}
