import { connect } from 'react-redux'
import { compose } from 'redux'

import SharePopinContent from './SharePopinContent'

const mapStateToProps = ({ share }) => ({ ...share })

export const SharePopin = compose(connect(mapStateToProps))(SharePopinContent)

export default SharePopin
