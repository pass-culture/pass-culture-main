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

  parseAvailableDate = date => {
    if (!date) return false
    const { availables } = this.props
    const format = 'YYYYMMDD'
    const formatted = date.format(format)
    const contains = availables.includes(formatted)
    return !contains
  }

  render() {
    const {
      help,
      name,
      label,
      format,
      disabled,
      availables,
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
                onChange={input.onChange}
                getCalendarContainer={() => this.container}
                disabledDate={availables && this.parseAvailableDate}
                placeholder={placeholder || moment().format(format)}
                className="calendarpicker-field-input"
                dropdownClassName="calendarpicker-field-popup"
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
  availables: null,
  defaultValue: '',
  disabled: false,
  format: 'DD MMMM YYYY',
  help: null,
  label: null,
  placeholder: null,
}

CalendarField.propTypes = {
  availables: PropTypes.array,
  defaultValue: PropTypes.string,
  disabled: PropTypes.bool,
  format: PropTypes.string,
  help: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
}

export default CalendarField
