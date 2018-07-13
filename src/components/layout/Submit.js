import React, {Component} from 'react'

class Submit extends Component {

  static defaultProps = {
    requiredFields: [],
    getDisabled: () => true,
    getTitle: () => null,
    type: 'submit',
  }

  render () {
    const {
      children,
      getTitle,
      getDisabled,
      ...otherProps,
    } = this.props
    return <button {...otherProps} title={getTitle()} disabled={getDisabled()}>{children}</button>
  }
}

export default Submit
