export const getAvailableBalanceByType = walletBalance => ({ actual, max }) => {
  const isvalid =
    typeof walletBalance === 'number' && typeof actual === 'number' && typeof max === 'number'
  if (!isvalid) return '--'
  const availableByType = max - actual
  return Math.min(walletBalance, availableByType)
}

export default getAvailableBalanceByType
