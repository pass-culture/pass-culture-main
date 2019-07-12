import classnames from 'classnames'
import moment from 'moment'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import DatePicker from 'react-datepicker'
import { Field } from 'react-final-form'
import { composeValidators } from 'react-final-form-utils'

import Icon from '../../Icon'
import getRequiredValidate from '../../form/utils/getRequiredValidate'

const renderReadOnlyDateInput = ({ formattedSelectedDatetime, name }) => ({
  propTypes: {
    formattedSelectedDatetime: PropTypes.string,
    name: PropTypes.string,
  },
  render() {
    return (
      <input
        className="field-input field-date"
        name={name}
        readOnly
        value={formattedSelectedDatetime}
      />
    )
  },
})

const renderDateInput = dateInputProps => (
  <div className="flex-columns items-center field-input field-date">
    <DatePicker {...dateInputProps} />
    <div className="flex-auto" />
    <Icon
      alt="Horaires"
      svg="ico-calendar"
    />
  </div>
)

function applyTimezoneToDatetime(inputValue, timezone) {
  let selectedDatetime

  selectedDatetime = moment(inputValue)
  if (timezone) {
    selectedDatetime = selectedDatetime.tz(timezone)
  }
  return selectedDatetime
}

function formatSelectedDatetime(inputValue, dateFormat) {
  return moment(inputValue).format(dateFormat)
}

export class DateField extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { hasPressedDelete: false }
  }

  onDateChange = input => date => {
    const changedValue = date ? date.toISOString() : null
    input.handleOnChange(changedValue)
    this.setState({ hasPressedDelete: false })
  }

  onKeyDown = input => event => {
    const isDeleteKey = event.keyCode === 8
    if (!isDeleteKey) return

    input.handleOnChange(null)
    this.setState({ hasPressedDelete: true })
  }

  renderField = ({ input }) => {
    const {
      className,
      clearable,
      dateFormat,
      id,
      label,
      locale,
      name,
      placeholder,
      readOnly,
      renderValue,
      required,
      timezone,
      // see github.com/Hacker0x01/react-datepicker/blob/master/docs/datepicker.md
      ...DatePickerProps
    } = this.props
    const inputName = id || name
    const isClearable = !readOnly && clearable
    const { hasPressedDelete } = this.state
    let formattedSelectedDatetime = null
    let selectedDatetime = null

    const shouldFormatDatetime = !hasPressedDelete && input.value
    if (shouldFormatDatetime) {
      selectedDatetime = applyTimezoneToDatetime(input.value, timezone)
      formattedSelectedDatetime = formatSelectedDatetime(selectedDatetime, dateFormat)
    }

    const dateInputProps = {
      className: 'date',
      dateFormat,
      id: inputName,
      isClearable,
      locale,
      placeholderText: placeholder,
      selected: selectedDatetime,
      shouldCloseOnSelect: true,
      ...DatePickerProps,
      ...input,
      onChange: this.onDateChange(input),
      onKeyDown: this.onKeyDown(input),
      value: formattedSelectedDatetime,
    }

    return (
      <div
        className={classnames('field date-field', className, {
          'is-read-only': readOnly,
        })}
        id={id}
      >
        <label
          className={classnames('field-label', { empty: !label })}
          htmlFor={name}
        >
          {label && (
            <span>
              <span>{label}</span>
              {required && !readOnly && <span className="field-asterisk">{'*'}</span>}
            </span>
          )}
        </label>
        <div className="field-control">
          <div className="field-value flex-columns items-center">
            <div className="field-inner flex-columns items-center">
              {readOnly
                ? renderReadOnlyDateInput({
                    formattedSelectedDatetime,
                    name,
                  })
                : renderDateInput(dateInputProps)}
            </div>
            {renderValue()}
          </div>
        </div>
      </div>
    )
  }

  render() {
    const {
      name,
      required,
      validate,
    } = this.props

    return (
      <Field
        name={name}
        render={this.renderField}
        validate={composeValidators(validate, getRequiredValidate(required))}
      />
    )
  }
}

DateField.defaultProps = {
  autoComplete: false,
  className: '',
  clearable: false,
  dateFormat: 'DD/MM/YYYY',
  datePickerClassName: 'date',
  disabled: false,
  id: null,
  label: '',
  locale: 'fr',
  placeholder: 'Please enter a value',
  readOnly: false,
  renderValue: () => null,
  required: false,
  timezone: null,
  validate: null,
}

DateField.propTypes = {
  autoComplete: PropTypes.bool,
  className: PropTypes.string,
  clearable: PropTypes.bool,
  dateFormat: PropTypes.string,
  datePickerClassName: PropTypes.string,
  disabled: PropTypes.bool,
  id: PropTypes.string,
  label: PropTypes.string,
  locale: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  renderValue: PropTypes.func,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  timezone: PropTypes.string,
  validate: PropTypes.func,
}

export default DateField
