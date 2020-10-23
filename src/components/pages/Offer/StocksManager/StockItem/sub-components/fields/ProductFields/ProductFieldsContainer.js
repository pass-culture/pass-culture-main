import { assignModalConfig } from 'pass-culture-shared'
import { connect } from 'react-redux'

import ProductFields from './ProductFields'

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
