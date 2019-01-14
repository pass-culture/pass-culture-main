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

const classNamePrefix = 'pc-final-form-selectbox'

const buildIdentifier = (index, parentIndex = null) => {
  // le splitter est utilisé par lodash.get
  // pour obtenir l'objet dans le provider passé en props
  const isnumber = typeof parentIndex === 'number'
  const splitter = (isnumber && '.options.') || ''
  const parent = (isnumber && `${parentIndex}`) || ''
  const identifier = `${parent}${splitter}${index}`
  return identifier
}

const renderOption = (object, index, parentIndex) => {
  const key = slugify(object.value)
  const identifier = buildIdentifier(index, parentIndex)
  return (
    <option
      value={identifier}
      key={`${key}::${identifier}`}
      className={`${classNamePrefix}__option`}
    >
      {object.label}
    </option>
  )
}

const renderOptionsGroup = (group, parentIndex) => {
  const key = slugify(group.label)
  return (
    <optgroup
      key={key}
      label={group.label}
      className={`${classNamePrefix}__optgroup`}
    >
      {group.options &&
        group.options.map((obj, index) =>
          renderOption(obj, index, parentIndex)
        )}
    </optgroup>
  )
}

class SelectBox extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { value: undefined }
  }

  onChange = input => event => {
    const { value } = event.target
    const { provider } = this.props
    const inputValue = get(provider, value)
    this.setState({ value }, () => input.onChange(inputValue))
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
            <label htmlFor={id || name} className={classNamePrefix}>
              {label && <InputLabel label={label} required={required} />}
              {help && <InputHelp label={help} />}
              <span className="pc-final-form-inner">
                <select
                  id={id || name}
                  disabled={disabled}
                  className="pc-final-form-input"
                  // recompose value/onchange input
                  {...input}
                  value={value}
                  onChange={this.onChange(input)}
                >
                  {placeholder && <option value={-1}>{placeholder}</option>}
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
              <FormError id={`${id || name}-error`} meta={meta} />
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
  help: null,
  id: null,
  label: null,
  required: false,
}

SelectBox.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool,
  help: PropTypes.string,
  id: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  provider: PropTypes.arrayOf(SelectboxObjectType).isRequired,
  required: PropTypes.bool,
}

export default SelectBox
