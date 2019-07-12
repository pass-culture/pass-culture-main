import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import { withSizes } from 'react-sizes'
import DatePicker from 'react-datepicker'

import InputLabel from '../InputLabel'

const DatePickerCustomInput = React.forwardRef((props, ref) => {
  const { readOnly, value } = props
  const hasvalue = value && typeof value === 'string' && value.trim() !== ''
  let cssclass = (hasvalue && 'selected') || ''
  cssclass = `${cssclass} ${(readOnly && 'read-only') || ''}`
  return (
    <div className={`react-datepicker__input-container_wrapper ${cssclass}`}>
      <input
        {...props}
        className="pc-final-form-datepicker-input"
        readOnly
        ref={ref}
      />
    </div>
  )
})

DatePickerCustomInput.defaultProps = {
  readOnly: false,
  value: null,
}

DatePickerCustomInput.propTypes = {
  readOnly: PropTypes.bool,
  value: PropTypes.string,
}

const buildPopperContainer = ({ current }) => ({ children }) => {
  if (!current) return null
  return ReactDOM.createPortal(children, current)
}

const DatePickerField = ({
  className,
  clearable,
  dateFormat,
  hideToday,
  id,
  label,
  locale,
  name,
  placeholder,
  provider,
  onChange,
  popperRefContainer,
  readOnly,
  required,
  // NOTE -> Autres props du react-datepicker passées en option
  // github.com/Hacker0x01/react-datepicker/blob/master/docs/datepicker.md
  ...rest
}) => {
  const moreprops = { ...rest }
  if (popperRefContainer) {
    moreprops.popperContainer = buildPopperContainer(popperRefContainer)
  }
  if (!hideToday) {
    moreprops.todayButton = `Aujourd'hui`
  }
  const isClearable = !readOnly && clearable
  const inputName = id || name
  return (
    <div className={`${className}`}>
      <label
        className="pc-final-form-datepicker"
        htmlFor={inputName}
      >
        {label && <InputLabel
          label={label}
          required={required}
                  />}
        <div className="pc-final-form-inner">
          <DatePicker
            customInput={<DatePickerCustomInput readOnly={readOnly} />}
            dateFormat={dateFormat}
            id={inputName}
            includeDates={provider}
            isClearable={isClearable}
            locale={locale}
            onChange={onChange}
            placeholderText={placeholder}
            readOnly={readOnly}
            shouldCloseOnSelect
            {...moreprops}
          />
        </div>
      </label>
    </div>
  )
}

DatePickerField.defaultProps = {
  className: '',
  clearable: true,
  dateFormat: 'DD/MM/YYYY',
  hideToday: false,
  icon: null,
  id: null,
  label: null,
  locale: 'fr',
  placeholder: 'Par date...',
  popperRefContainer: null,
  provider: null,
  readOnly: false,
  required: false,
  withPortal: false,
}

DatePickerField.propTypes = {
  className: PropTypes.string,
  clearable: PropTypes.bool,
  dateFormat: PropTypes.string,
  hideToday: PropTypes.bool,
  icon: PropTypes.string,
  id: PropTypes.string,
  label: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
  locale: PropTypes.string,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  popperRefContainer: PropTypes.shape(),
  provider: PropTypes.arrayOf(PropTypes.shape()),
  readOnly: PropTypes.bool,
  required: PropTypes.bool,
  withPortal: PropTypes.bool,
}

const mapSizesToProps = ({ height }) => ({
  withPortal: height <= 650,
})

export default withSizes(mapSizesToProps)(DatePickerField)
