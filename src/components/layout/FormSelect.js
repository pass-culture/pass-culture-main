import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import classnames from 'classnames'
import get from 'lodash.get'

import { removeErrors } from '../../reducers/errors'
import { getFormValue, mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'

class FormSelect extends Component {

  handleMergeForm (defaultValue) {
    const {
      collectionName,
      entityId,
      mergeForm,
      name
    } = this.props
    if (defaultValue && entityId === NEW) {
      mergeForm(collectionName, entityId, name, defaultValue)
    }
  }

  componentDidMount () {
    this.handleMergeForm(this.props.defaultValue)
  }

  componentDidUpdate (prevProps) {
    if (this.props.defaultValue !== prevProps.defaultValue) {
      this.handleMergeForm(this.props.defaultValue)
    }
  }

  componentWillMount() {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, method } = this.props
    defaultValue && method === 'POST' && this.handleMergeForm(defaultValue)
  }

  onChange = ({ target: { value } }) => {
    const {
      collectionName,
      entityId,
      mergeForm,
      name,
      removeErrors
    } = this.props
    removeErrors(name)
    mergeForm(collectionName, entityId, name, value)
  }

  render() {
    const {
      className,
      options,
      readOnly,
      value
    } = this.props
    const defaultReadOnly = readOnly || get(this.props, 'options', []).length === 1
    return (
      <div className={classnames('select', {readonly: defaultReadOnly}, className)}>
        <select
          readOnly={defaultReadOnly}
          onChange={this.onChange}
          value={value}
        >
          {
            options && options.filter(o => o).map(({ label, value }, index) =>
              <option key={index} value={value}>
                {label}
              </option>
            )
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
  { mergeForm, removeErrors }
)(FormSelect)
