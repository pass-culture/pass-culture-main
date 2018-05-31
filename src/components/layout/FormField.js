import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import FormSelect from './FormSelect'
import FormTextarea from './FormTextarea'
import Icon from './Icon'

const FormComponentsByName = {
  FormInput,
  FormSelect,
  FormTextarea
}

class FormField extends Component {
  render() {
    const {
      className,
      collectionName,
      errors,
      id,
      label,
      name,
      type,
    } = this.props
    const inputId = id || `input_${collectionName}_${name}`
    const extraProps = {
      className: classnames(className, `input ${type}`),
    }
    const labelMarkup = (
      <label htmlFor={inputId} key={'label_' + id}>
        {label}
      </label>
    )
    const inputComponentName = `Form${type[0].toUpperCase()}${type.slice(1)}`
    console.log('inputComponentName', inputComponentName)
    const InputComponent = FormComponentsByName[inputComponentName] || FormInput
    const inputMarkup = <InputComponent
      {...this.props}
      {...extraProps}
      id={inputId}
      key={inputId}
      aria-describedby={`${inputId}-error`}
    />
    return [
      <div
        className={classnames('form-input', {
          checkbox: type === 'checkbox',
        })}
        key={0}
      >
        {type === 'checkbox'
          ? [inputMarkup, labelMarkup]
          : [labelMarkup, inputMarkup]}
      </div>,
      <ul role='alert' id={`${inputId}-error`} className={classnames('errors', { pop: errors })} key={1}>
        {errors &&
          errors.map((e, index) => (
            <li key={index}>
              <Icon svg="picto-warning" alt="Warning" /> {e}
            </li>
          ))}
      </ul>,
    ]
  }
}

FormField.defaultProps = {
  type: 'input'
}

FormField.propTypes = {
  collectionName: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired
}

export default compose(
  connect((state, ownProps) => ({
    errors: state.data.errors && state.data.errors[ownProps['name']],
  }))
)(FormField)
