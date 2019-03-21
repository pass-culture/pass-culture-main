/* eslint
  react/jsx-one-expression-per-line: 0 */
import { connect } from 'react-redux'
import RawActivationPassword from './RawActivationPassword'
import { mapDispatchToProps, mapStateToProps } from './connect'

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(RawActivationPassword)
