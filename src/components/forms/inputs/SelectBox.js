import React from 'react'
import Select from 'react-select'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import InputLabel from '../InputLabel'

const formatOptions = (options, format) =>
  (format &&
    options.map(obj => ({
      label: obj[format.label || 'label'],
      value: obj[format.value || 'value'],
    }))) ||
  options

class SelectBox extends React.PureComponent {
  render() {
    const {
      className,
      disabled,
      format,
      id,
      label,
      name,
      provider,
      required,
      // props from https://react-select.com/props
      ...reactSelectAPIProps
    } = this.props
    const options = formatOptions(provider, format)
    return (
      <Field
        name={name}
        render={({ input, meta }) => (
          <div className={`pc-final-form-selectbox ${className}`}>
            <label htmlFor={id || name} className="pc-final-form-text">
              {label && <InputLabel label={label} required={required} />}
              <Select
                options={options}
                classNamePrefix="pc-final-form-selectbox"
                isDisabled={disabled || reactSelectAPIProps.isDisabled || false}
                isSearchable={reactSelectAPIProps.isSearchable || true}
                isClearable={reactSelectAPIProps.isClearable || true}
                autoFocus={reactSelectAPIProps.autoFocus || false}
                {...reactSelectAPIProps}
                {...input}
              />
              <FormError meta={meta} />
            </label>
          </div>
        )}
      />
    )
  }
}

SelectBox.defaultProps = {
  className: '',
  disabled: false,
  format: null,
  id: null,
  label: null,
  required: false,
}

SelectBox.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool,
  format: PropTypes.object,
  id: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  provider: PropTypes.array.isRequired,
  required: PropTypes.bool,
}

export default SelectBox
