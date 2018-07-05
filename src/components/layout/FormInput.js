import debounce from 'lodash.debounce'
import React, { Component } from 'react'
import { connect } from 'react-redux'

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
    this.onDebouncedMergeForm({
      target: {
          value: (type === 'checkbox' || type === 'radio')
            ? event.target.checked
            : event.target.value
      }
    })
    this.setState({ localValue: event.target.value })
    onChange && onChange(event)
  }

  onMergeForm = event => {
    const {
      target: { value },
    } = event
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
    if (type === 'checkbox' || type === 'radio') {
      mergedValue = value ? (defaultValue || true) : false
    } else if (type === 'number') {
      mergedValue = Number(value)
    } else {
      mergedValue = storeValue(value)
    }
    removeErrors(name)
    mergeForm(collectionName, entityId, name, mergedValue, parentValue)
  }

  componentDidMount() {
    // fill automatically the form when it is a NEW POST action
    const { entityId, defaultValue } = this.props
    typeof defaultValue !== 'undefined' && entityId === NEW &&
      this.onMergeForm({ target: { value: defaultValue } })
  }

  componentDidUpdate (prevProps) {
    const {
      defaultValue,
      entityId
    } = this.props
    if (typeof defaultValue !== 'undefined' && defaultValue !== prevProps.defaultValue) {
      entityId === NEW && this.onMergeForm({ target: { value: defaultValue } })
    }
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
    const formatedValue = formatValue(
      localValue !== null
        ? localValue
        : typeof value !== 'undefined'
          ? value
          : typeof defaultValue !== 'undefined'
            ? defaultValue
            : ''
    )
    return (
      <input
        autoComplete={autoComplete}
        className={className || 'input'}
        id={id}
        onChange={this.onChange}
        placeholder={placeholder}
        readOnly={readOnly}
        required={required}
        type={type}
        value={formatedValue}
      />
    )
  }
}

FormInput.defaultProps = {
  debounceTimeout: 500,
  type: 'text',
  entityId: NEW,
  formatValue: v => v,
  storeValue: v => v,
}

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { mergeForm, removeErrors }
)(FormInput)
