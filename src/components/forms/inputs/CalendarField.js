import React from 'react'
import moment from 'moment'
import PropTypes from 'prop-types'
import { DatePicker, Form } from 'antd'
import { Field } from 'react-final-form'
// import momentPropTypes from 'react-moment-proptypes'
import locale from 'antd/lib/date-picker/locale/fr_FR'

import renderLabel from '../renderLabel'

const momentIsSameDay = (a, b) => a && b && a.isSame(b, 'day')

export class CalendarField extends React.PureComponent {
  constructor(props) {
    super(props)
    this.popupContainer = null
  }

  setContainerRef = ref => {
    this.popupContainer = ref
  }

  filterDisabledDate = currDate => {
    const { provider } = this.props
    if (!currDate) return false
    // si une date n'est pas dans le provider
    // -> elle ne sera pas affichée dans le calendrier
    const result = provider.filter(s => momentIsSameDay(currDate, s))
    return result && !result.length
  }

  render() {
    const {
      help,
      name,
      label,
      disabled,
      provider,
      className,
      dateFormat,
      placeholder,
      ...rest
    } = this.props
    return (
      <Form.Item
        {...rest}
        label={renderLabel(label, help)}
        className={`calendarpicker-field ${className}`}
      >
        <Field
          name={name}
          render={({ input }) => (
            <DatePicker
              size="large"
              // style={customize input box style}
              // popupStyle={customize popup calendar style}
              // dateRender={custom rendering function for date cells}
              className="calendarpicker-field-input"
              dropdownClassName="calendarpicker-field-popup"
              locale={locale}
              format={dateFormat}
              disabled={disabled}
              getCalendarContainer={() => this.popupContainer}
              placeholder={placeholder || moment().format(dateFormat)}
              // specify the dates that cannot be selected
              disabledDate={provider && this.filterDisabledDate}
              // a la selection de l'user d'une date
              // on renvoi les valeurs du calendar
              // { date: Moment, dateString: String }
              onChange={(date, dateString) =>
                input.onChange({ date, dateString })
              }
            />
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
  className: '',
  dateFormat: 'DD MMMM YYYY',
  defaultValue: '',
  disabled: false,
  help: null,
  label: null,
  placeholder: null,
  provider: null,
}

const providerObjectsShape = PropTypes.shape({
  // FIXME -> using array(PropTypes.shape) and
  // momentPropTypes as PropTypes throws error
  date: PropTypes.string,
  value: PropTypes.string,
})

CalendarField.propTypes = {
  className: PropTypes.string,
  dateFormat: PropTypes.string,
  defaultValue: PropTypes.string,
  disabled: PropTypes.bool,
  help: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  provider: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.string),
    PropTypes.arrayOf(providerObjectsShape),
  ]),
}

export default CalendarField
