import { connect } from 'react-redux'

import DownloadButton from './DownloadButton'
import mapDispatchToProps from './mapDispatchToProps'

export default connect(
  null,
  mapDispatchToProps
)(DownloadButton)
