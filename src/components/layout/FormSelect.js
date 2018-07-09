import classnames from 'classnames'
import get from 'lodash.get'
import { removeErrors, NEW } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { getFormValue, mergeForm } from '../../reducers/form'

class FormSelect extends Component {

  handleMergeForm = () => {
    const {
      collectionName,
      defaultValue,
      entityId,
      mergeForm,
      name
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
      defaultValue,
      options,
      readOnly,
      value
    } = this.props
    const defaultReadOnly = readOnly || get(this.props, 'options', []).length === 1

    return (
      <div className={classnames('select', {readonly: defaultReadOnly}, className)}>
        <select
          disabled={defaultReadOnly} // readonly doesn't exist on select
          onChange={this.onChange}
          value={value || defaultValue}
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
