import debounce from 'lodash.debounce'
import PropTypes from 'prop-types'
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
    console.log('event', event.target.value)
    this.handleDebouncedMergeForm(event)
    this.setState({ localValue: event.target.value })
  }
  handleMergeForm = ({ target: { value } }) => {
    const { collectionName, id, mergeForm, name, type } = this.props
    // be sure to cast to the good type
    const mergedValue = type === 'number'
      ? Number(value)
      : value
    // merge
    mergeForm(collectionName, id, name, mergedValue)
  }
  componentWillMount () {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, id } = this.props
    defaultValue && id === NEW && this.handleMergeForm(defaultValue)
  }
  render () {
    const { className,
      defaultValue,
      isRequired,
      placeholder,
      type,
      value
    } = this.props
    const { localValue } = this.state
    return (
      <span>
        <input className={className || 'input'}
          onChange={this.onChange}
          placeholder={placeholder}
          type={type}
          value={
            localValue !== null
            ? localValue
            : value || defaultValue || ''
          } />
        {isRequired && <span className='form-input__required'> (*) </span>}
      </span>
    )
  }
}

FormInput.defaultProps = {
  debounceTimeout: 500,
  id: NEW
}

FormInput.propTypes = {
  collectionName: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired
}

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { mergeForm }
)(FormInput)
