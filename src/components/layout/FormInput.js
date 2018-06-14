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
    const { type, onChange } = this.props
    event.persist()
    this.onDebouncedMergeForm(event.target.value)
    this.setState({ localValue: event.target.value })
    onChange && onChange(event)
  }

  onMergeForm = value => {
    const {
      collectionName,
      defaultValue,
      entityId,
      mergeForm,
      name,
      parentValue,
      storeValue,
      removeErrors,
      type
    } = this.props
    let mergedValue
    if (type === 'number') {
      mergedValue = Number(value)
    } else {
      mergedValue = storeValue(value)
    }
    removeErrors(name)
    mergeForm(collectionName, entityId, name, mergedValue, parentValue)
  }

  componentDidUpdate (prevProps) {
    if (this.props.defaultValue !== prevProps.defaultValue) {
      this.onMergeForm(this.props.defaultValue)
    }
  }

  componentWillMount() {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, method } = this.props
    defaultValue && method === 'POST' && this.onMergeForm(defaultValue)
  }

  render() {
    const {
      className,
      defaultValue,
      id,
      placeholder,
      autoComplete,
      readOnly,
      required,
      type,
      value,
      formatValue,
    } = this.props
    const { localValue } = this.state
    return (
      type !== 'switch'
      ? (
        <input
          readOnly={readOnly}
          required={required}
          autoComplete={autoComplete}
          className={className || 'input'}
          id={id}
          onChange={this.onChange}
          placeholder={placeholder}
          type={type}
          value={formatValue(localValue !== null ? localValue : value || defaultValue || '')}
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
  formatValue: v => v,
  storeValue: v => v,
}

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { mergeForm, removeErrors }
)(FormInput)
