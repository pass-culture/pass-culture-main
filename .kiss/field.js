import React from 'react'
import PropTypes from 'prop-types'
import { Form } from 'antd'
import { Field } from 'react-final-form'

import renderLabel from '../renderLabel'

export class FormField extends React.PureComponent {
  constructor(props) {
    super(props)
  }

  render() {
    const { help, name, label, disabled, ...rest } = this.props
    return (
      <Form.Item
        {...rest}
        label={renderLabel(label, help)}
        className={`noop-input ${rest.className || ''}`}>
        <Field name={name} type="text" component="input" />
      </Form.Item>
    )
  }
}

FormField.defaultProps = {
  disabled: false,
  help: null,
  label: null,
}

FormField.propTypes = {
  disabled: PropTypes.bool,
  help: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
}

export default FormField
