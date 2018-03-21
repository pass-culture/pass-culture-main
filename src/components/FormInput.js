import debounce from 'lodash.debounce'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { getFormValue, mergeForm } from '../reducers/form'
import { NEW } from '../utils/config'

class FormInput extends Component {
  constructor (props) {
    super (props)
    this.state = { localValue: null }
    this.handleDebouncedMergeForm = debounce(
      this.handleMergeForm,
      props.debounceTimeout
    )
  }
  onChange = event => {
    event.persist()
    this.handleDebouncedMergeForm(event)
    this.setState({ localValue: event.target.value })
  }
  handleMergeForm = ({ target: { value } }) => {
    const { collectionName, entityId, mergeForm, name, type } = this.props
    // be sure to cast to the good type
    const mergedValue = type === 'number'
      ? Number(value)
      : value
    // merge
    mergeForm(collectionName, entityId, name, mergedValue)
  }
  componentWillMount () {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, entityId } = this.props
    defaultValue && entityId === NEW && this.handleMergeForm(defaultValue)
  }
  render () {
    const { className,
      defaultValue,
      id,
      placeholder,
      type,
      value
    } = this.props
    const { localValue } = this.state
    return (
        <input className={className || 'input'}
          id={id}
          onChange={this.onChange}
          placeholder={placeholder}
          type={type}
          value={
            localValue !== null
            ? localValue
            : value || defaultValue || ''
          } />
    )
  }
}

FormInput.defaultProps = {
  debounceTimeout: 500,
  entityId: NEW
}

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { mergeForm }
)(FormInput)
