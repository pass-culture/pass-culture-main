import { connect } from 'react-redux'
import ProductFields from './ProductFields'
import { assignModalConfig } from 'pass-culture-shared'

export const mapDispatchToProps = dispatch => {
  return {
    assignModalConfig: (extraClassName) => {
      dispatch(
        assignModalConfig(
          {extraClassName}
        )
      )
    }
  }
}

export default connect(
  null,
  mapDispatchToProps
)(ProductFields)
