import { connect } from 'react-redux'

import Overlay from './Overlay'

export const mapStateToProps = ({ overlay, share }) => ({
  isVisible: overlay || share.visible,
})

export default connect(mapStateToProps)(Overlay)
