import React from 'react'
import moment from 'moment'
import PropTypes from 'prop-types'
import { DatePicker, Form } from 'antd'
import { Field } from 'react-final-form'
import locale from 'antd/lib/date-picker/locale/fr_FR'

import renderLabel from '../renderLabel'

export class CalendarField extends React.PureComponent {
  constructor(props) {
    super(props)
    this.container = null
  }

  setContainerRef = ref => {
    this.container = ref
  }

  render() {
    const {
      help,
      name,
      label,
      format,
      disabled,
      provider,
      placeholder,
      ...rest
    } = this.props
    return (
      <Form.Item
        {...rest}
        label={renderLabel(label, help)}
        className="calendarpicker-field"
      >
        <Field
          name={name}
          render={({ input }) => (
            <React.Fragment>
              <DatePicker
                format={format}
                locale={locale}
                disabled={disabled}
                disabledDate={() => false}
                // defaultValue={input.value.date}
                getCalendarContainer={() => this.container}
                placeholder={placeholder || moment().format(format)}
                className="calendarpicker-field-input"
                dropdownClassName="calendarpicker-field-popup"
                onChange={(date, dateString) => {
                  input.onChange({ date, dateString })
                }}
              />
            </React.Fragment>
          )}
        />
        <div
          ref={this.setContainerRef}
          className="calendarpicker-field-popup-container is-relative"
        />
      </Form.Item>
    )
  }
}

CalendarField.defaultProps = {
  defaultValue: '',
  disabled: false,
  format: 'DD MMMM YYYY',
  help: null,
  label: null,
  placeholder: null,
  provider: null,
}

CalendarField.propTypes = {
  defaultValue: PropTypes.string,
  disabled: PropTypes.bool,
  format: PropTypes.string,
  help: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  provider: PropTypes.array,
}

export default CalendarField
