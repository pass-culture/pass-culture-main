import { connect } from 'react-redux'
import { compose } from 'redux'
import PropTypes from 'prop-types'

import selectIsFeatureActive from '../../../../router/selectors/selectIsFeatureActive'

const mapStateToProps = state => ({
  isFeatureFlipped: selectIsFeatureActive(state, 'NEW_RIBS_UPLOAD'),
})

const RibsUploadFeatureFlip = compose(
  connect(mapStateToProps)
)(({ isFeatureFlipped, children, legacy }) => (isFeatureFlipped ? children : legacy))

RibsUploadFeatureFlip.propTypes = {
  children: PropTypes.node,
  legacy: PropTypes.node,
}

export default RibsUploadFeatureFlip
