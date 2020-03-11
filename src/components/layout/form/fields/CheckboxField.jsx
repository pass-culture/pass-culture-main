import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

class CheckboxField extends PureComponent {
  renderField = ({ input }) => {
    const {
      checked,
      id,
      label,
    } = this.props

    return (
      <div>
        <input
          {...input}
          defaultChecked={checked}
          id={id}
          type="checkbox"
        />
        { label && (
          <label htmlFor={id}>
            {label}
          </label>
        )}
      </div>
    )
  }

  render() {
    const { name } = this.props

    return (
      <Field
        name={name}
        render={this.renderField}
      />
    )
  }
}

CheckboxField.defaultProps = {
  checked: true,
  label: '',
}

CheckboxField.propTypes = {
  checked: PropTypes.bool,
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
}

export default CheckboxField
