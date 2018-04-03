import FormInput from '../components/FormInput'
import FormTextarea from '../components/FormTextarea'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'

class FormField extends Component {
  render () {
    const {
      collectionName,
      errors,
      id,
      label,
      name,
      required,
      type
    } = this.props
    const inputId = id || 'input_'+collectionName+'_'+name
    const labelMarkup = ( <label htmlFor={id} key={'label_'+id}>
                          { label }
                          { required && <span className='form-input__required'> (*) </span>}
                        </label> )
    const inputMarkup = type === 'textarea' ? ( <FormTextarea {...this.props} id={inputId} key={inputId} /> ) : ( <FormInput {...this.props} id={inputId} key={inputId} /> )
    return (
        <div className='form-input'>
          {
            type === 'checkbox'
              ? [inputMarkup, labelMarkup]
              : [ labelMarkup, inputMarkup ]
          }
          <ul className='form-input__errors'>
            {
              errors && errors.map((e, index) => (
                <li key={index}>{e}</li>
              ))
            }
          </ul>
        </div>
    )
  }
}

FormInput.propTypes = {
  collectionName: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired
}

export default compose(
  connect(
    (state, ownProps) => ({
      errors: state.data.errors && state.data.errors[ownProps['name']]
    }),
  )
)(FormField)
