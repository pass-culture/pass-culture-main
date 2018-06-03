import debounce from 'lodash.debounce'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import SwitchButton from './SwitchButton'
import { removeErrors } from '../../reducers/errors'
import { getFormValue, mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'

class FormInput extends Component {
  constructor(props) {
    super(props)
    this.state = {
      localValue: null,
    }
    this.onDebouncedMergeForm = debounce(
      this.onMergeForm,
      props.debounceTimeout
    )
  }

  onChange = event => {
    const { type } = this.props
    event.persist()
    this.onDebouncedMergeForm(event)
    if (type === 'checkbox' || type === 'radio' || 'type' === 'switch') {
      return
    }
    this.setState({ localValue: event.target.value })
  }

  onMergeForm = event => {
    const {
      target: { checked, value },
    } = event
    const {
      collectionName,
      defaultValue,
      entityId,
      mergeForm,
      name,
      parentValue,
      removeErrors,
      type
    } = this.props
    let mergedValue
    if (type === 'checkbox' || type === 'radio') {
      mergedValue = checked ? (defaultValue || true) : false
    } else if (type === 'switch') {
      mergedValue = value
    } else if (type === 'number') {
      mergedValue = Number(value)
    } else {
      mergedValue = value
    }
    removeErrors(name)
    mergeForm(collectionName, entityId, name, mergedValue, parentValue)
  }

  componentWillMount() {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, entityId } = this.props
    defaultValue &&
      entityId === NEW &&
      this.onMergeForm({ target: { value: defaultValue } })
  }

  render() {
    const {
      className,
      defaultValue,
      id,
      placeholder,
      autoComplete,
      required,
      type,
      value,
    } = this.props
    const { localValue } = this.state
    return (
      type !== 'switch'
      ? (
        <input
          required={required}
          autoComplete={autoComplete}
          className={className || 'input'}
          id={id}
          onChange={this.onChange}
          placeholder={placeholder}
          type={type}
          value={localValue !== null ? localValue : value || defaultValue || ''}
        />
      )
      : (
        <SwitchButton {...this.props}
          isInitialActive={defaultValue}
          onClick={this.onChange}
        />
      )
    )
  }
}

FormInput.defaultProps = {
  debounceTimeout: 500,
  entityId: NEW,
}

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { mergeForm, removeErrors }
)(FormInput)
