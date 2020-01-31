const getAvailableBalanceByType = walletBalance => ({ actual, max }) => {
  const maximumAvailableByType = max - actual
  const actualAvailableByType = Math.min(walletBalance, maximumAvailableByType)
  return actualAvailableByType
}

export default getAvailableBalanceByType