const onTimeUpdates = (selectedStockId, name, allFormValues) => {
  const resetObj = {}
  const isValid =
    selectedStockId &&
    typeof selectedStockId === 'string' &&
    allFormValues &&
    allFormValues.stockId &&
    typeof allFormValues.stockId === 'string' &&
    allFormValues.bookables &&
    Array.isArray(allFormValues.bookables)
  if (!isValid) return resetObj
  const { bookables } = allFormValues
  const { price, id: stockId } = bookables.find(bookable => bookable.id === selectedStockId)
  return { isDuo: false, price, stockId }
}

export default onTimeUpdates
