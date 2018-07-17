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
      isPasswordHidden: true,
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
      case 'email':
        return 'email'
      case 'password':
        return 'password'
      case 'time':
        return 'time'
      case 'date':
        return 'date'
      case 'siren':
        return 'siren'
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
    if (type === 'checkbox') {
      return {
        displayValue: v => v,
        storeValue: v => Boolean(v),
      }
    }
    if (type === 'number') {
      return {
        displayValue: v => (v || ''),
        storeValue: v => (parseInt(v, 10) || ''),
      }
    }
    return {
      displayValue: v => (v || ''),
      storeValue: v => v,
    }
  }

  static getDerivedStateFromProps({autoComplete, name, type, required, readonly}) {
    type = type || Field.guessInputType(name) // Would be cleaner to use `this` instead of `Field` but doesn't work :(
    return {
      required: required && !readonly,
      type,
      autoComplete: autoComplete || Field.guessAutoComplete(name, type),
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

  onChange = (value) => {
    if (value === this.props.value) {
      return
    }
    const { displayValue, storeValue } = this.state

    this.setState({
      value: displayValue(value),
    }, () => {
      this.props.onChange(this.props.name, storeValue(value))
    })
  }

  toggleHidden = e => {
    e.preventDefault()
    this.setState({
      isPasswordHidden: !this.state.isPasswordHidden
    })
  }

  onInputChange = e => this.onChange(this.props.type === 'checkbox' ? e.target.checked : e.target.value)

  renderInput = () => {
    const {
      id,
      name,
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

    const commonProps = {
      'aria-describedby': `${id}-error`,
      autoComplete,
      id,
      name,
      onChange: this.onInputChange,
      placeholder,
      readOnly,
      required,
      value,
    }

    switch(type) {
      case 'date':
        return readOnly ? (
          <span> {value && value.format(this.props.dateFormat)} </span>
          ) : (
          <div className={`input is-${size} date-picker`}>
            <DatePicker
              className='date'
              filterDate={this.props.filterDate}
              highlightDates={this.props.highlightedDates || []}
              minDate={this.props.minDate || moment()}
              onChange={this.onChange}
              selected={value ? moment(value) : null}
            />
            <Icon
              alt='Horaires'
              className="input-icon"
              svg="ico-calendar"
            />
          </div>
        )

      case 'password':
        if (this.props.noPasswordToggler) break;
        return <div className="field has-addons password">
          <div className="control is-expanded">
            <input {...commonProps} className={`input is-${size}`} type={this.state.isPasswordHidden ? 'password' : 'text'} />
          </div>
          <div className="control">
            <button className="button is-rounded is-medium" onClick={this.toggleHidden}>
              <Icon svg={this.state.isPasswordHidden ? 'ico-eye close' : 'ico-eye'} />
              &nbsp;
            </button>
          </div>
        </div>

      case 'siren':
      case 'siret':
        if (typeof this.props.fetchedName !== 'string') break;
        return <div className='with-display-name'>
          <input {...commonProps} className={`input is-${size}`} />
          <div className='display-name'>{this.props.fetchedName}</div>
        </div>

      case 'select':
        const actualReadOnly = readOnly || this.props.options.length === 1
        const actualOptions = optionify(this.props.options.map(o => ({label: get(o, this.props.optionLabel), value: get(o, this.props.optionValue)})), placeholder)
        return <div className={`select is-${size} ${classnames({readonly: actualReadOnly})}`}>
          <select
            {...commonProps}
            disabled={actualReadOnly} // readonly doesn't exist on select
            >
            { actualOptions.filter(o => o).map(({ label, value }, index) =>
              <option key={index} value={value}>
                {label}
              </option>
            )}
          </select>
        </div>

      case 'checkbox':
        return <label
          className={`${classnames({required})}`}
          htmlFor={id}
        >
          <input {...commonProps} type='checkbox' className='input'  />
          {this.props.label}
        </label>

      case 'textarea':
        return <Textarea {...commonProps} className={`textarea is-${size}`} />

      default:
        break;
    }
    return <input {...commonProps} type={type} className={`input is-${size}`} min={type === 'number' ? this.props.min || 0 : null} />
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
    const {
      type
    } = this.state
    const $input = this.renderInput()

    if (this.state.type === 'hidden') return $input
    switch(layout) {
      case 'horizontal':
        return <div className='field is-horizontal'>
          {label && <div className={`field-label is-${size}`}>
            <label htmlFor={id} className='label'><span className={`subtitle ${classnames({required, readOnly})}`}>{label} :</span></label>
          </div>}
          <div className='field-body'>
            <div className={`field ${classnames({'is-expanded': isExpanded})}`}>
              {$input}
            </div>
            {errors.map((e, i) => <p className='help is-danger' id={`${id}-error`} key={i}>
              <Icon svg="picto-warning" alt="Warning" /> {e}
            </p>)}
          </div>
        </div>
      case 'sign-in-up':
        if (type === 'checkbox') {
          return <div className='field checkbox'>{$input}</div>
        } else {
          const {sublabel} = this.props
          return <div className="field">
            {label && <label className='label' htmlFor={id}>
              <h3 className={classnames({required, 'with-subtitle': sublabel})}>{label}</h3>
              {sublabel && <p>... {sublabel} :</p>}
            </label>}
            <div className="control">
              {$input}
            </div>
            <ul className="help is-danger" id={`${id}-error`}>
              {errors.map((e, i) => <li key={i}><Icon svg="picto-warning" alt="Warning" /> {e}</li>)}
            </ul>
          </div>
        }
      default:
        break
    }
    return $input
  }

  render() {
    return this.renderLayout()
  }
}

export default Field
