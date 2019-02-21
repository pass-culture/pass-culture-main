const DEFAULT_FALLBACK = '--'

const getWalletValue = (user, fallback = DEFAULT_FALLBACK) => {
  const isValid = user && typeof user.wallet_balance === 'number'
  if (!isValid) return fallback
  return user.wallet_balance
}

export default getWalletValue
