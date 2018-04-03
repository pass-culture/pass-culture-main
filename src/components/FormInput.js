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
    const { type } = this.props
    event.persist()
    console.log(this.$input.value)
    this.handleDebouncedMergeForm(event)
    if (type === 'checkbox' || type === 'radio' ) {
      return
    }
    this.setState({ localValue: event.target.value })
  }
  handleMergeForm = (evt) => {
    const { target: { checked, value } } = evt
    const { collectionName, defaultValue, entityId, mergeForm, name, type } = this.props
    let mergedValue
    if (type === 'checkbox' || type === 'radio' ) {
      mergedValue = checked ? ( defaultValue || true ) : false
    } else if (type === 'number') {
      mergedValue = Number(value)
    } else {
      mergedValue = value
    }
    // merge
    mergeForm(collectionName, entityId, name, mergedValue)
  }
  componentWillMount () {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, entityId } = this.props
    defaultValue && entityId === NEW && this.handleMergeForm({target : { value : defaultValue}})
  }
  componentDidMount () {
    this.$input.addEventListener('change', () => {
      if ($this.$input.value) {
        this.handleMergeForm($this.$input.value)
      }
    })
  }
  componentWillUnmount () {
    
  }
  render () {
    const {
      className,
      defaultValue,
      id,
      placeholder,
      autoComplete,
      type,
      value
    } = this.props
    const { localValue } = this.state
    return (
      <input autoComplete={autoComplete}
        className={className || 'input'}
        id={id}
        onChange={this.onChange}
        placeholder={placeholder}
        ref={$e => this.$input = $e}
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
