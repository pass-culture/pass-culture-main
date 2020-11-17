import { Selector } from 'testcafe'

const getUserWalletValue = async () => {
  const classWalletValue = '.ph-wrapper .ph-wallet-balance'
  const profileWalletValue = await Selector(classWalletValue).textContent
  const value = profileWalletValue.replace('€', '')
  return parseFloat(value)
}

export const getVersoWalletValue = async () => {
  const classWalletValue = '.verso-wallet-amount'
  const profileWalletValue = await Selector(classWalletValue).textContent
  const value = profileWalletValue.replace('€', '')
  return parseFloat(value)
}

export default getUserWalletValue
