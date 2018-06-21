import React, {Component} from 'react'
import { connect } from 'react-redux'

import get from 'lodash.get'

class Submit extends Component {

  render () {
    const {
      children,
      className,
      getTitle,
      isDisabled,
    } = this.props
    return <button type='submit' title={getTitle()} disabled={isDisabled()} className={className}>{children}</button>
  }
}


Submit.defaultProps = {
  requiredFields: [],
  isDisabled: () => true,
  getTitle: () => null,
}

export default Submit
