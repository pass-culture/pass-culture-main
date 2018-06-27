import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import Textarea from 'react-autosize-textarea';

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
    const { className, defaultValue, id, placeholder, required, value, readOnly, } = this.props
    return (

      <Textarea
        required={required}
        className={className || 'textarea'}
        id={id}
        onChange={this.onChange}
        placeholder={placeholder}
        value={value || defaultValue || ''}
        readOnly={readOnly}
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
