import { connect } from 'react-redux'

import SharePopin from './SharePopin'

const mapStateToProps = ({ share }) => ({ ...share })

export default connect(mapStateToProps)(SharePopin)
