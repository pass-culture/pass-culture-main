import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import FormList from './FormList'
import FormPassword from './FormPassword'
import FormSearch from './FormSearch'
import FormSelect from './FormSelect'
import FormSirene from './FormSirene'
import FormTextarea from './FormTextarea'
import Icon from './Icon'
import { capitalize } from '../../utils/string'

const FormComponentsByName = {
  FormInput,
  FormList,
  FormSearch,
  FormSelect,
  FormPassword,
  FormSirene,
  FormTextarea
}

class FormField extends Component {

  render() {
    const {
      className,
      collectionName,
      controlClassName,
      errors,
      id,
      inputClassName,
      label,
      labelClassName,
      name,
      type,
      readOnly,
      required,
    } = this.props

    const inputId = id || `input_${collectionName}_${name}`
    const isCheckbox = type === 'checkbox';
    const InputComponent = FormComponentsByName[`Form${capitalize(type)}`] || FormInput
    const inputMarkup = <InputComponent
      {...this.props}
      className={classnames({
        checkbox: type === 'checkbox',
        input: type !== 'textarea' && type !== 'select',
        textarea: type === 'textarea',
      }, className, inputClassName)}
      id={inputId}
      key={inputId}
      aria-describedby={`${inputId}-error`}
      readOnly={readOnly}
    />
    const labelMarkup = (
      <label className={classnames({
        checkbox: isCheckbox,
        label: !isCheckbox,
        required,
      }, labelClassName)} htmlFor={inputId} key={'label_' + inputId}>
        { isCheckbox && inputMarkup }
        {label}
      </label>
    )
    return [
      <div
        className={classnames('form-field field', {
          checkbox: isCheckbox,
        })}
        key={0}
      >
        <div className={classnames('control', controlClassName)}>
          { isCheckbox && labelMarkup }
          { !isCheckbox && [labelMarkup, inputMarkup]}
        </div>
        <ul role='alert'
          id={`${inputId}-error`}
          className={classnames('errors', { pop: errors })}
          key={1}
        >
          {errors &&
            errors.map((e, index) => (
              <li key={index}>
                <Icon svg="picto-warning" alt="Warning" /> {e}
              </li>
            ))}
        </ul>
      </div>
    ]
  }
}

FormField.defaultProps = {
  type: 'input'
}

FormField.propTypes = {
  collectionName: PropTypes.string.isRequired
}

export default compose(
  connect((state, ownProps) => ({
    errors: state.errors[ownProps['name']],
  }))
)(FormField)
