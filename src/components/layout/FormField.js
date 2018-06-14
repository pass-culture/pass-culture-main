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

  static propTypes = {
    collectionName: PropTypes.string.isRequired
  }

  static defaultProps = {
    size: 'normal',
  }

  render() {
    const {
      className,
      collectionName,
      controlClassName,
      error,
      id,
      inputClassName,
      isExpanded,
      isHorizontal,
      label,
      labelClassName,
      name,
      size,
      type,
      readOnly,
      required,
    } = this.props

    const inputId = id || `input_${collectionName}_${name}`
    const isCheckbox = type === 'checkbox';
    const isSelect = type === 'select';
    const InputComponent = FormComponentsByName[`Form${capitalize(type)}`] || FormInput
    let inputMarkup = <InputComponent
      {...this.props}
      className={classnames({
        checkbox: isCheckbox,
        input: type !== 'textarea' && !isSelect,
        textarea: type === 'textarea',
        'is-rounded': !isCheckbox,
      }, className, inputClassName)}
      id={inputId}
      key={inputId}
      aria-describedby={`${inputId}-error`}
      readOnly={readOnly}
    />

    if (!isCheckbox) {
      inputMarkup = <div className='control is-expanded' key={`control_${inputId}`}>{inputMarkup}</div>
    }

    let labelMarkup = (
      <label className={classnames({
        checkbox: isCheckbox,
        label: !isCheckbox,
        required,
      }, labelClassName)} htmlFor={inputId} key={`label_${inputId}`}>
        { isCheckbox && inputMarkup }
        {label}
      </label>
    )
    if (isHorizontal) {
      labelMarkup = (
        <div className={`field-label is-${size}`} key={`field_label_${inputId}`}>
          {labelMarkup}
        </div>
      )
      inputMarkup = (
        <div className='field-body' key={`field_body_${inputId}`}>
          <div className={`field ${isExpanded ? 'is-expanded' : 'is-narrow'}`}>
            {inputMarkup}
          </div>
        </div>
      )
    }
    return [
      <div
        className={classnames('form-field field', {
          checkbox: isCheckbox,
          'is-horizontal': isHorizontal,
        })}
        key={0}
      >
        { isCheckbox ? labelMarkup : [labelMarkup, inputMarkup] }
        <ul role='help is-danger'
          id={`${inputId}-error`}
          className={classnames('error', { pop: error })}
          key={1}
        >
          {
            error && (
              <p>
                <Icon svg="picto-warning" alt="Warning" /> {error}
              </p>
            )
          }
        </ul>
      </div>
    ]
  }
}

export default compose(
  connect((state, ownProps) => ({
    error: state.errors[ownProps['name']],
  }))
)(FormField)
