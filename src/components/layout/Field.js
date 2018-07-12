import React, {Component} from 'react'
import PropTypes from 'prop-types';
import classnames from 'classnames'
import get from 'lodash.get'
import { removeWhitespaces, formatSiren } from '../../utils/string'
import Icon from './Icon'
import { optionify } from '../../utils/form'
import Textarea from 'react-autosize-textarea'
import DatePicker from 'react-datepicker'
import moment from 'moment'


class Field extends Component {

  constructor(props) {
    super(props)
    this.state = {
      value: '',
    }
  }

  static defaultProps = {
    onChange: () => {},
    dateFormat: 'DD/MM/YYYY',
    layout: 'horizontal',
    size: 'normal',
    optionValue: 'id',
    optionLabel: 'name',
  }

  static propTypes = {
    name: PropTypes.string.isRequired,
  }

  static guessInputType(name) {
    switch(name) {
      case 'time':
        return 'time'
      case 'date':
        return 'date'
      case 'siren':
        return 'text'
      case 'price':
        return 'number'
      default:
        return 'text'
    }

  }

  static guessAutoComplete(name, type) {
    return type || name
  }

  static guessFormatters(name, type) {
    if (name === 'siren' || name === 'siret') {
      return {
        displayValue: formatSiren,
        storeValue: removeWhitespaces,
      }
    }
    return {
      displayValue: v => (v || ''),
      storeValue: v => v,
    }
  }

  static getDerivedStateFromProps({name, type, required, readonly}) {
    type = type || Field.guessInputType(name) // Would be cleaner to use `this` instead of `Field` but doesn't work :(
    return {
      required: required && !readonly,
      type,
      autoComplete: Field.guessAutoComplete(name, type),
      ...Field.guessFormatters(name, type),
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
    if (!value) return
    const {displayValue, storeValue} = this.state
    this.setState({
      value: displayValue(value),
    })
    this.props.onChange(this.props.name, storeValue(value))
  }

  onInputChange = e => this.onChange(e.target.value)

  renderInput = () => {
    const {
      id,
      name,
      onChange,
      optionLabel,
      optionValue,
      placeholder,
      readOnly,
      size,
    } = this.props

    const {
      autoComplete,
      required,
      type,
      value,
    } = this.state


    switch(type) {
      case 'date':
        console.log(this.props.highlightDates)
        return readOnly ? (
          <span> {value && value.format(this.props.dateFormat)} </span>
          ) : (
          <div className={`input is-${size} date-picker`}>
            <DatePicker
              key={0}
              className='date'
              filterDate={this.props.filterDate}
              highlightDates={this.props.highlightedDates || []}
              minDate={this.props.minDate || moment()}
              onChange={this.onChange}
              selected={value ? moment(value) : null}
            />,
            <Icon
              key={1}
              alt='Horaires'
              className="input-icon"
              svg="ico-calendar"
            />
          </div>
        )
      case 'select':
        const actualReadOnly = readOnly || this.props.options.length === 1
        const actualOptions = optionify(this.props.options.map(o => ({label: get(o, optionLabel), value: get(o, optionValue)})), placeholder)
        return <div className={`select is-${size} ${classnames({readonly: actualReadOnly})}`}>
          <select
            autoComplete={autoComplete}
            disabled={actualReadOnly} // readonly doesn't exist on select
            id={id}
            name={name}
            onChange={this.onInputChange}
            placeholder={placeholder}
            required={required}
            value={value}          >
            { actualOptions.filter(o => o).map(({ label, value }, index) =>
              <option key={index} value={value}>
                {label}
              </option>
            )}
          </select>
        </div>
      case 'textarea':
        return <Textarea
          autoComplete={autoComplete}
          className={`textarea is-${size}`}
          id={id}
          name={name}
          onChange={this.onInputChange}
          placeholder={placeholder}
          readOnly={readOnly}
          required={required}
          value={value}
        />
      default:
        return <input
          autoComplete={autoComplete}
          className={`input is-${size}`}
          id={id}
          name={name}
          onChange={this.onInputChange}
          placeholder={placeholder}
          readOnly={readOnly}
          required={required}
          type={type}
          value={value}
          min={this.props.min || 0}
        />
    }
  }

  renderLayout() {
    const {
      errors,
      id,
      isExpanded,
      label,
      layout,
      required,
      readOnly,
      size,
    } = this.props
    const $input = this.renderInput()

    if (this.state.type === 'hidden') return $input
    switch(layout) {
      case 'horizontal':
        return <div className={`field is-horizontal ${classnames({required, readOnly})}`}>
          {label && <div className={`field-label is-${size}`}>
            <label htmlFor={id} className='label'><span className='subtitle'>{label} :</span></label>
          </div>}
          <div className='field-body'>
            <div className={`field ${classnames({'is-expanded': isExpanded})}`}>
              {$input}
            </div>
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