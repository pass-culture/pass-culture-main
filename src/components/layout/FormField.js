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
import FormSiret from './FormSiret'
import FormThumb from './FormThumb'
import FormTextarea from './FormTextarea'
import Icon from './Icon'
import { capitalize } from '../../utils/string'

const FormComponentsByName = {
  FormInput,
  FormList,
  FormSearch,
  FormSelect,
  FormPassword,
  FormSiret,
  FormTextarea,
  FormThumb
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
      required,
    } = this.props
    const inputId = id || `input_${collectionName}_${name}`
    const isCheckbox = type === 'checkbox';
    const InputComponent = FormComponentsByName[`Form${capitalize(type)}`] || FormInput
    const inputMarkup = <InputComponent
      {...this.props}
      className={classnames(className, {
        checkbox: type === 'checkbox',
        input: type !== 'textarea' && type !== 'select',
        textarea: type === 'textarea',
      })}
      id={inputId}
      key={inputId}
      aria-describedby={`${inputId}-error`}
    />
    const labelMarkup = (
      <label className={classnames({
        checkbox: isCheckbox,
        label: !isCheckbox,
        required: required,
      })} htmlFor={inputId} key={'label_' + inputId}>
        { isCheckbox && inputMarkup }
        {label}
      </label>
    )
    return [
      <div
        className={classnames({
          field: true,
          checkbox: isCheckbox,
        })}
        key={0}
      >
        <div className='control'>
          { isCheckbox && labelMarkup }
          { !isCheckbox && [labelMarkup, inputMarkup]}
        </div>
        <ul role='alert' id={`${inputId}-error`} className={classnames('errors', { pop: errors })} key={1}>
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
