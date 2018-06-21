import React, { Component } from 'react'

import Icon from './Icon'
import FormInput from './FormInput'

class FormPassword extends Component {
  constructor() {
    super()
    this.state = {
      isHidden: true,
    }
  }

  toggleHidden = e => {
    e.preventDefault()
    this.setState({
      isHidden: !this.state.isHidden
    })
  }

  static defaultProps = {
    showPassword: true,
  }

  render() {
    const input = <FormInput {...this.props} type={this.state.isHidden ? 'password' : 'text'} />;
    if (!this.props.showPassword) {
      return input
    }

    return (
      <div className="field has-addons password">
        <div className="control is-expanded">
          {input}
        </div>
        <div className="control">
          <button className="button is-rounded is-medium" onClick={this.toggleHidden}>
            <Icon svg={this.state.isHidden ? 'ico-eye close' : 'ico-eye'} />
            &nbsp;
          </button>
        </div>
      </div>
    )
  }
}

export default FormPassword
