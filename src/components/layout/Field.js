import React, {Component} from 'react'
import classnames from 'classnames'
import get from 'lodash.get'
import { removeWhitespaces, formatSiren } from '../../utils/string'
import Icon from './Icon'
import { optionify } from '../../utils/form'
import Textarea from 'react-autosize-textarea'

class Field extends Component {

  constructor() {
    super()
    this.state = {
      value: '',
    }
  }

  static defaultProps = {
    onChange: () => {},
    layout: 'horizontal',
    size: 'normal',
    optionValue: 'id',
    optionLabel: 'name',
  }

  static nameToInputType(name) {
    switch(name) {
      case 'siren':
        return 'text'
      default:
        return 'text'
    }

  }

  static nameToAutoComplete(type, name) {
    return type || name
  }

  static nameToFormatter(name) {
    switch(name) {
      case 'siren':
      case 'siret':
        return {
          displayValue: formatSiren,
          storeValue: removeWhitespaces,
        }
      default:
        return {
          displayValue: v => (v || ''),
          storeValue: v => v,
        }
    }
  }

  componentDidMount() {
    this.onChange(this.props.value)
  }

  componentDidUpdate(prevProps) {
    if (prevProps.value !== this.props.value) {
      this.onChange(this.props.value)
    }
  }

  onChange = value => {
    const {displayValue, storeValue} = this.constructor.nameToFormatter(this.props.name)
    this.setState({
      value: displayValue(value),
    })
    this.props.onChange(this.props.name, storeValue(value))
  }

  onInputChange = e => this.onChange(e.target.value)

  renderInput = () => {
    const {
      autoComplete,
      id,
      errors,
      label,
      name,
      onChange,
      options,
      optionLabel,
      optionValue,
      placeholder,
      readOnly,
      required,
      type,
      value,
    } = this.props

    const actualType = type || this.constructor.nameToInputType(name)
    const actualAutoComplete = autoComplete || this.constructor.nameToAutoComplete(type, name)
    const actualRequired = required && !readOnly

    switch(actualType) {
      case 'select':
        const actualReadOnly = readOnly || options.length === 1
        const actualOptions = optionify(options.map(o => ({label: get(o, optionLabel), value: get(o, optionValue)})), placeholder)
        return <div className={`select ${classnames({readonly: actualReadOnly})}`}>
          <select
            autoComplete={actualAutoComplete}
            id={id}
            onChange={this.onInputChange}
            required={actualRequired}
            disabled={actualReadOnly} // readonly doesn't exist on select
            placeholder={placeholder}
            value={this.state.value}
          >
            { actualOptions.filter(o => o).map(({ label, value }, index) =>
              <option key={index} value={value}>
                {label}
              </option>
            )}
          </select>
        </div>
      case 'textarea':
        return <Textarea
          autoComplete={actualAutoComplete}
          id={id}
          placeholder={placeholder}
          value={this.state.value}
          onChange={this.onInputChange}
          required={actualRequired}
          readOnly={readOnly}
          className='textarea'
        />
      default:
        return <input
          autoComplete={actualAutoComplete}
          type={actualType}
          id={id}
          className='input'
          onChange={this.onInputChange}
          required={actualRequired}
          readOnly={readOnly}
          placeholder={placeholder}
          value={this.state.value}
        />
    }
  }

  renderLayout() {
    const {
      errors,
      id,
      label,
      layout,
      required,
      readOnly,
      size,
      type,
    } = this.props
    const $input = this.renderInput()
    if (type === 'hidden') return $input
    switch(layout) {
      case 'horizontal':
        return <div className={`field is-horizontal ${classnames({required, readOnly})}`}>
          {label && <div className={`field-label is-${size}`}>
            <label htmlFor={id} className='label'><span className='subtitle'>{label} :</span></label>
          </div>}
          <div className='field-body'>
            {$input}
            {errors.map(e => <p className='help is-danger'>
              <Icon svg="picto-warning" alt="Warning" /> {e}
            </p>)}
          </div>
        </div>
      default:
        return $input
    }
    return $input
  }

  render() {
    return this.renderLayout()
  }
}

export default Field