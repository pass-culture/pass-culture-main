import classnames from 'classnames'
import FormInput from '../components/FormInput'
import FormTextarea from '../components/FormTextarea'
import Icon from '../components/Icon'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'

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
      className: classnames(className, `input input--${type} ${type}`),
    }
    const labelMarkup = (
      <label htmlFor={id} key={'label_' + id}>
        {label}
      </label>
    )
    const inputMarkup =
      type === 'textarea' ? (
        <FormTextarea
          {...this.props}
          {...extraProps}
          id={inputId}
          key={inputId}
        />
      ) : (
        <FormInput {...this.props} {...extraProps} id={inputId} key={inputId} />
      )
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
