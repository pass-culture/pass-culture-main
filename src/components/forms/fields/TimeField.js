import React from 'react'
import PropTypes from 'prop-types'
import { Form, TimePicker } from 'antd'
import { Field } from 'react-final-form'
import renderLabel from '../renderLabel'

export class TimeField extends React.PureComponent {
  constructor(props) {
    super(props)
    this.container = null
  }

  setContainerRef = ref => {
    this.container = ref
  }

  render() {
    const { help, name, label, disabled, format, ...rest } = this.props
    return (
      <Form.Item
        {...rest}
        label={renderLabel(label, help)}
        className="timepicker-field"
      >
        <Field
          name={name}
          render={input => (
            <TimePicker
              allowEmpty
              inputReadOnly
              hideDisabledOptions
              format={format}
              onChange={input.onChange}
              className="timepicker-field-input"
              dropdownClassName="timepicker-field-popup"
              getPopupContainer={() => this.container}
            />
          )}
        />
        <div
          ref={this.setContainerRef}
          className="timepicker-field-popup-container is-relative"
        />
      </Form.Item>
    )
  }
}
TimeField.defaultProps = {
  disabled: false,
  format: 'HH:mm',
  help: null,
  label: null,
}
TimeField.propTypes = {
  disabled: PropTypes.bool,
  format: PropTypes.string,
  help: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
}
export default TimeField
