import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { getFormValue, mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'

class FormSelect extends Component {
  componentWillMount() {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, method } = this.props
    defaultValue && method === 'POST' && this.handleMergeForm(defaultValue)
  }

  onChange = ({ target: { value } }) => {
    const { collectionName, entityId, mergeForm, name, maxLength } = this.props
    mergeForm(collectionName, entityId, name, value)
  }

  render() {
    const { className,
      defaultValue,
      id,
      name,
      options,
      type,
      value
    } = this.props
    return (
      <div className={'select'}>
        <select
          className=''
          value={typeof value === 'string' ? value : defaultValue}
          onChange={this.onChange}
        >
          {
            options && options.map((option, index) => (
              <option key={index} value={option.value}>
                {option.label}
              </option>))
          }
        </select>
      </div>
    )
  }
}

FormSelect.defaultProps = {
  entityId: NEW
}

FormSelect.propTypes = {
  collectionName: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
}

export default connect(
  (state, ownProps) => ({
    value: getFormValue(state, ownProps),
  }),
  { mergeForm }
)(FormSelect)
