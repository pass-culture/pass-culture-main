export const getAvailableBalanceByType = walletBalance => ({ actual, max }) => {
  const maximumAvailableByType = max - actual
  const actualAvailableByType = Math.min(walletBalance, maximumAvailableByType)
  return formatDecimals(actualAvailableByType)
}

const formatDecimals = number => {
  const numberWithTwoDecimals = number.toFixed(2)
  return numberWithTwoDecimals.replace('.00', '')
}

export default getAvailableBalanceByType
