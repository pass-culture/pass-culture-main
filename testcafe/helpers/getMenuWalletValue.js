import { Selector } from 'testcafe'

const getMenuWalletValue = async () => {
  const id = '#main-menu-header-wallet-value'
  const menuWalletValue = await Selector(id).textContent
  const value = menuWalletValue.replace('€', '')
  return parseFloat(value)
}

export default getMenuWalletValue
