import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'

import FormDate from './FormDate'
import FormGeo from './FormGeo'
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
  FormDate,
  FormGeo,
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
      withDisplayName,
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
      }, inputClassName)}
      id={inputId}
      key={inputId}
      aria-describedby={`${inputId}-error`}
      readOnly={readOnly}
      withDisplayName={withDisplayName}
    />

    if (!isCheckbox) {
      inputMarkup = (
        <div className='control' key={`control_${inputId}`}>
          {inputMarkup}
        </div>
      )
    }

    let labelMarkup = (
      <label
        className={classnames({
          checkbox: isCheckbox,
          label: !isCheckbox,
          required,
        }, labelClassName)}
        htmlFor={inputId}
        key={`label_${inputId}`}
      >
        { isCheckbox && inputMarkup }
        {label}
      </label>
    )

    const errorMarkup = (
      <ul
        id={`${inputId}-error`}
        className={classnames('help', 'is-danger', { pop: error })}
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
            {errorMarkup}
          </div>
        </div>
      )
    } else {
      inputMarkup = [inputMarkup, errorMarkup]
    }

    return [
      <div
        className={classnames('form-field field', {
          checkbox: isCheckbox,
          'is-horizontal': isHorizontal,
        }, className)}
        key={0}
      >
        { isCheckbox ? labelMarkup : [labelMarkup, inputMarkup] }
      </div>
    ]
  }
}

export default compose(
  connect((state, ownProps) => ({
    error: state.errors[ownProps['name']],
  }))
)(FormField)
