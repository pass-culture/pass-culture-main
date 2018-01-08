import React, { Component } from 'react'
import { connect } from 'react-redux'

import { assignForm } from '../reducers/form'

class InputForm extends Component {
  constructor () {
    super()
    this.onChange = this._onChange.bind(this)
  }
  _onChange ({ target: { value } }) {
    const { assignForm, name } = this.props
    assignForm({ [name]: value })
  }
  render () {
    return <input className='input'
      onChange={this.onChange} />
  }
}

export default connect(null, { assignForm })(InputForm)
