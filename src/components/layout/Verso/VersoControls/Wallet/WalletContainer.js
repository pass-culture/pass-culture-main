import { connect } from 'react-redux'
import { selectCurrentUser } from 'with-react-redux-login'

import Wallet from './Wallet'
import { getWalletValue } from '../../../../../utils/user'

export const mapStateToProps = state => {
  const currentUser = selectCurrentUser(state)
  const value = getWalletValue(currentUser)
  return { value }
}

export default connect(mapStateToProps)(Wallet)
