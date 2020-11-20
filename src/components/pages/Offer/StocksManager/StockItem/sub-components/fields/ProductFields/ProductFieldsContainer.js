import { connect } from 'react-redux'

import { assignModalConfig } from 'store/reducers/modal'

import ProductFields from './ProductFields'

export const mapDispatchToProps = dispatch => {
  return {
    assignModalConfig: extraClassName => {
      dispatch(assignModalConfig({ extraClassName }))
    },
  }
}

export default connect(null, mapDispatchToProps)(ProductFields)
