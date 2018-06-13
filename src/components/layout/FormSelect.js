import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { getFormValue, mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'

class FormSelect extends Component {

  handleMergeForm () {
    const {
      collectionName,
      defaultValue,
      entityId,
      mergeForm,
      name,
      options
    } = this.props
    if (defaultValue && entityId === NEW) {
      mergeForm(collectionName, entityId, name, defaultValue)
    }
  }

  componentDidMount () {
    this.handleMergeForm()
  }

  componentDidUpdate (prevProps) {
    if (this.props.defaultValue !== prevProps.defaultValue) {
      this.handleMergeForm()
    }
  }

  componentWillMount() {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, method } = this.props
    defaultValue && method === 'POST' && this.handleMergeForm(defaultValue)
  }

  onChange = ({ target: { value } }) => {
    const { collectionName, entityId, mergeForm, name } = this.props
    mergeForm(collectionName, entityId, name, value)
  }

  render() {
    const { className,
      defaultValue,
      options,
      readOnly,
      value
    } = this.props
    return (
      <div className={className || 'select'}>
        <select
          className=''
          disabled={readOnly}
          onChange={this.onChange}
          value={typeof value === 'string' ? value : defaultValue}
        >
          {
            options && options.map(({ label, value }, index) => (
              <option key={index} value={value}>
                {label}
              </option>
            ))
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
