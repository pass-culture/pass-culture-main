import { Selector } from 'testcafe'

const id = '#verso-wallet-value'

export const getVersoWallet = async () => {
  const versoWallet = await Selector(id).textContent
  return versoWallet
}

export const getVersoWalletValue = async () => {
  const versoWallet = await getVersoWallet()
  const value = versoWallet.replace('€', '')
  return parseFloat(value)
}
