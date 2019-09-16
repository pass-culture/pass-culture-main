import { withRouter } from 'react-router'
import withSizes from 'react-sizes'
import { compose } from 'redux'

import VersoHeader from './VersoHeader'

export const mapSizeToProps = ({ width, height }) => ({
  height,
  width: Math.min(width, 500),
})

export default compose(
  withRouter,
  withSizes(mapSizeToProps)
)(VersoHeader)
