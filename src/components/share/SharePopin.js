import { compose } from 'redux'
import { connect } from 'react-redux'

import SharePopinContent from './SharePopinContent'

const mapStateToProps = ({ share }) => ({ ...share })

export const SharePopin = compose(connect(mapStateToProps))(SharePopinContent)

export default SharePopin
