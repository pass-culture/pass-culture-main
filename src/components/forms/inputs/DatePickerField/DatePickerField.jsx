import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import { withSizes } from 'react-sizes'
import DatePicker from 'react-datepicker'

import DatePickerCustomField from './DatePickerCustomField/DatePickerCustomField'
import InputLabel from '../../InputLabel'

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
  const moreProps = { ...rest }
  if (popperRefContainer) {
    moreProps.popperContainer = buildPopperContainer(popperRefContainer)
  }
  if (!hideToday) {
    moreProps.todayButton = `Aujourd'hui`
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
            {...moreProps}
            customInput={
              <DatePickerCustomField
                ref={popperRefContainer}
              />
            }
            dateFormat={dateFormat}
            id={inputName}
            includeDates={provider}
            isClearable={isClearable}
            locale={locale}
            onChange={onChange}
            placeholderText={placeholder}
            readOnly={readOnly}
            shouldCloseOnSelect
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
