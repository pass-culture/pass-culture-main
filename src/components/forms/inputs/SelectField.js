import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Field } from 'react-final-form'

import InputLabel from '../InputLabel'
import Icon from '../../layout/Icon'

class SelectField extends PureComponent {
  constructor(props) {
    super(props)
    this.popupContainer = null
  }

  getPopupContainer = () => {
    return () => this.popupContainer
  }

  setContainerRef = ref => {
    this.popupContainer = ref
  }

  renderSelect = ({ input }) => {
    const { disabled, id, options, placeholder, readOnly, ...rest } = this.props
    const hasNoOption = !options.length
    const isDisabled = disabled || hasNoOption || readOnly

    const moreProps = { ...rest }
    if (id) moreProps.id = id

    const { onChange, value } = input

    return (
      <div className={classnames('select-field pc-final-form-inner', { 'is-read-only': readOnly })}>
        <select
          {...moreProps}
          className="content"
          disabled={isDisabled}
          getPopupContainer={this.getPopupContainer()}
          onBlur={onChange}
          onChange={onChange}
          placeholder={placeholder}
          readOnly={readOnly}
          value={value}
        >
          {options &&
            options.map(option => (
              <option
                key={option.id}
                value={option.id}
              >
                {option.label}
              </option>
            ))}
        </select>
        {!readOnly && <Icon
          alt="Horaires"
          svg="ico-hour-list"
                      />}
      </div>
    )
  }

  render() {
    const { className, id, label, name, required } = this.props
    const inputName = id || name

    return (
      <div className={className}>
        <label
          className="pc-final-form-datepicker"
          htmlFor={inputName}
        >
          {label && <InputLabel
            label={label}
            required={required}
                    />}
          <Field
            name={name}
            render={this.renderSelect}
          />
          <div
            className="select-field-popup-container is-relative"
            ref={this.setContainerRef}
          />
        </label>
      </div>
    )
  }
}

SelectField.defaultProps = {
  className: '',
  disabled: false,
  id: null,
  label: null,
  placeholder: null,
  readOnly: false,
  required: false,
}

SelectField.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool,
  id: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  required: PropTypes.bool,
}

export default SelectField
