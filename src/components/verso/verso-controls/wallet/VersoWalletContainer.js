/* eslint
  react/jsx-one-expression-per-line: 0 */
import { connect } from 'react-redux'

import VersoWallet from './VersoWallet'
import { selectCurrentUser } from '../../../hocs'
import { getWalletValue } from '../../../../utils/user'

export const mapStateToProps = state => {
  const currentUser = selectCurrentUser(state)
  const value = getWalletValue(currentUser)
  return { value }
}

export default connect(mapStateToProps)(VersoWallet)
