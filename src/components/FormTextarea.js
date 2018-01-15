import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { getFormEntity, getFormValue, mergeForm } from '../reducers/form'
import { NEW } from '../utils/config'

class FormTextarea extends Component {
  componentWillReceiveProps(nextProps) {
    console.log('nextProps', nextProps)
    if (nextProps.isEmptyForm && !this.props.isEmptyForm) {
      console.log('BEN ALORS')
      // this._element.empty()
    }
  }
  onChange = ({ target: { value } }) => {
    const { collectionName, id, mergeForm, name, maxLength } = this.props
    if (value.length < maxLength) {
      mergeForm(collectionName, id, name, value)
    } else {
      console.warn('value reached maxLength')
    }
  }
  render () {
    const { className, defaultValue, placeholder, type, value } = this.props
    console.log('value', value)
    return <textarea className={className || 'textarea'}
      onChange={this.onChange}
      placeholder={placeholder}
      ref={_element => this._element = _element}
      type={type}
      value={value || defaultValue} />
  }
}

FormTextarea.defaultProps = {
  id: NEW,
  maxLength: 200
}

FormTextarea.propTypes = {
  collectionName: PropTypes.string.isRequired,
  id: PropTypes.string,
  name: PropTypes.string.isRequired
}

export default connect(
  (state, ownProps) => ({
    isEmptyForm: (getFormEntity(state, ownProps) || {}).length === 0,
    value: getFormValue(state, ownProps)
  }),
  { mergeForm }
)(FormTextarea)
