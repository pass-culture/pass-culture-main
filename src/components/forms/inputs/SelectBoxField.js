/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import InputHelp from '../InputHelp'
import InputLabel from '../InputLabel'
import { slugify } from '../../../utils/strings'
import { SelectboxObjectType } from '../../../types'

const CLASSNAME_PREFIX = 'pc-final-form-selectbox'

const renderOption = (object, identifier) => {
  const keySalt = slugify(object.value)
  return (
    <option
      className={`${CLASSNAME_PREFIX}__option`}
      key={`${keySalt}::${identifier}`}
      value={identifier}
    >
      {object.label}
    </option>
  )
}

const renderOptionsGroup = (group, groupIndex) => {
  const groupkey = slugify(group.label)
  return (
    <optgroup
      className={`${CLASSNAME_PREFIX}__optgroup`}
      key={groupkey}
      label={group.label}
    >
      {group.options &&
        group.options.map((obj, optionIndex) => {
          const splitter = '.options.'
          const identifier = `${groupIndex}${splitter}${optionIndex}`
          return renderOption(obj, identifier)
        })}
    </optgroup>
  )
}

const PLACEHOLDER_OPTION_VALUE = 'placeholder_option_value'

class SelectBoxField extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { value: undefined }
  }

  onChange = input => event => {
    const { value } = event.target
    const { provider, placeholder } = this.props
    const isDefaultOption = value === PLACEHOLDER_OPTION_VALUE
    const shouldResetForm = placeholder && isDefaultOption
    if (shouldResetForm) {
      // NOTE undefined reset le form
      // et desactive le bouton submit
      this.setState({ value }, () => input.onChange(undefined))
      return
    }
    const inputValue = get(provider, value)
    this.setState({ value }, () => input.onChange(inputValue))
  }

  renderPlaceHolderOption = () => {
    const { placeholder } = this.props
    return <option value={PLACEHOLDER_OPTION_VALUE}>{placeholder}</option>
  }

  render() {
    const {
      className,
      disabled,
      help,
      id,
      label,
      name,
      provider,
      placeholder,
      required,
    } = this.props
    const { value } = this.state
    return (
      <Field
        name={name}
        render={({ input, meta }) => (
          <div className={`${className}`}>
            <label
              className={CLASSNAME_PREFIX}
              htmlFor={id || name}
            >
              {label && <InputLabel
                label={label}
                required={required}
                        />}
              {help && <InputHelp label={help} />}
              <span className="pc-final-form-inner">
                <select
                  className="pc-final-form-input"
                  disabled={disabled}
                  id={id || name}
                  // recompose value/onchange input
                  {...input}
                  onChange={this.onChange(input)}
                  value={value}
                >
                  {placeholder && this.renderPlaceHolderOption()}
                  {provider &&
                    provider.map((obj, index) => {
                      const isgroup = obj && obj.options
                      const renderer = isgroup
                        ? renderOptionsGroup
                        : renderOption
                      return renderer(obj, index)
                    })}
                </select>
              </span>
              <FormError
                id={`${id || name}-error`}
                meta={meta}
              />
            </label>
          </div>
        )}
      />
    )
  }
}

SelectBoxField.defaultProps = {
  className: '',
  disabled: false,
  help: null,
  id: null,
  label: null,
  placeholder: null,
  required: false,
}

SelectBoxField.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool,
  help: PropTypes.string,
  id: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  provider: PropTypes.arrayOf(SelectboxObjectType).isRequired,
  required: PropTypes.bool,
}

export default SelectBoxField
