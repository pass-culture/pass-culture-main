import { compose } from 'redux'
import { connect } from 'react-redux'

import SharePopinContent from './SharePopinContent'

const mapStateToProps = ({ user, share }) => {
  const email = (user && user.email) || ''
  return { email, ...share }
}

export const SharePopin = compose(connect(mapStateToProps))(SharePopinContent)

export default SharePopin
