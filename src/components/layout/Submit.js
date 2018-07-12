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
      type,
      onClick
    } = this.props
    return <button onClick={onClick} type={type} title={getTitle()} disabled={isDisabled()} className={className}>{children}</button>
  }
}


Submit.defaultProps = {
  requiredFields: [],
  isDisabled: () => true,
  getTitle: () => null,
  type: 'submit',
}

export default Submit
