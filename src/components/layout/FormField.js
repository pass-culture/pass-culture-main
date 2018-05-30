import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'

import FormInput from './FormInput'
import FormPassword from './FormPassword'
import FormTextarea from './FormTextarea'
import Icon from './Icon'

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
    const inputMarkup =
      type === 'textarea' ? (
        <FormTextarea
          {...this.props}
          id={inputId}
          key={inputId}
        />
      ) : (
        type === 'password' ? ( <FormPassword {...this.props} id={inputId} key={inputId} />) :
        <FormInput {...this.props} id={inputId} key={inputId} />
      )
      const labelMarkup = (
        <label className={classnames(isCheckbox ? 'checkbox' : 'label', {required: required})} htmlFor={inputId} key={'label_' + inputId}>
          { isCheckbox && inputMarkup }
          {label}
        </label>
      )
    return [
      <div
        className={`field ${type}`}
        key={0}
      >
        <div className='control'>
          {
            isCheckbox
            ? labelMarkup
            : [labelMarkup, inputMarkup]
          }
        </div>
      </div>,
      <ul className={classnames('errors', { pop: errors })} key={1}>
        {errors &&
          errors.map((e, index) => (
            <li key={index}>
              <Icon svg="picto-warning" /> {e}
            </li>
          ))}
      </ul>,
    ]
  }
}

FormInput.propTypes = {
  collectionName: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
}

export default compose(
  connect((state, ownProps) => ({
    errors: state.data.errors && state.data.errors[ownProps['name']],
  }))
)(FormField)
