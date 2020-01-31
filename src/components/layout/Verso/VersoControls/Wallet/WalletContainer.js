import { connect } from 'react-redux'
import { selectCurrentUser } from 'with-react-redux-login'

import Wallet from './Wallet'
import formatDecimals from '../../../../../utils/numbers/formatDecimals'

export const mapStateToProps = state => {
  const currentUser = selectCurrentUser(state)
  const { wallet_balance } = currentUser

  const value = formatDecimals(wallet_balance)
  return { value }
}

export default connect(mapStateToProps)(Wallet)
