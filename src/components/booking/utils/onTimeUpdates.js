const onTimeUpdates = (selectedStockId, name, allFormValues) => {
  const resetObj = {}
  const isvalid =
    selectedStockId &&
    typeof selectedStockId === 'string' &&
    allFormValues &&
    allFormValues.stockId &&
    typeof allFormValues.stockId === 'string' &&
    allFormValues.bookables &&
    Array.isArray(allFormValues.bookables)
  if (!isvalid) return resetObj
  const { bookables } = allFormValues
  const { price, id: stockId } = bookables.find(o => o.id === selectedStockId)
  return { price, stockId }
}

export default onTimeUpdates
