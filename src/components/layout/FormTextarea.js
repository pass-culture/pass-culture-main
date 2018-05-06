import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { getFormValue, mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'

class FormTextarea extends Component {
  componentWillMount() {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, method } = this.props
    defaultValue && method === 'POST' && this.handleMergeForm(defaultValue)
  }

  onChange = ({ target: { value } }) => {
    const { collectionName, entityId, mergeForm, name, maxLength } = this.props
    if (value.length < maxLength) {
      mergeForm(collectionName, entityId, name, value)
    } else {
      console.warn('value reached maxLength')
    }
  }
  
  render() {
    const { className, defaultValue, id, placeholder, type, value } = this.props
    return (
      <textarea
        className={className || 'textarea'}
        id={id}
        onChange={this.onChange}
        placeholder={placeholder}
        ref={_element => (this._element = _element)}
        type={type}
        value={value || defaultValue || ''}
      />
    )
  }
}

FormTextarea.defaultProps = {
  entityId: NEW,
  maxLength: 200,
}

FormTextarea.propTypes = {
  collectionName: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
}

export default connect(
  (state, ownProps) => ({
    value: getFormValue(state, ownProps),
  }),
  { mergeForm }
)(FormTextarea)
