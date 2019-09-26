import formatDecimals from '../numbers/formatDecimals'

const getWalletValue = user => {
  if (user) {
    return formatDecimals(user.wallet_balance)
  }
}

export default getWalletValue
