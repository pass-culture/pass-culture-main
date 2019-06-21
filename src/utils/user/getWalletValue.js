const getWalletValue = (user, fallback = '--') =>
  user && typeof user.wallet_balance === 'number'
    ? user.wallet_balance
    : fallback

export default getWalletValue
