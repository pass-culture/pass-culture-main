import React, {Component} from 'react'
import PropTypes from 'prop-types';
import classnames from 'classnames'
import get from 'lodash.get'
import Icon from './Icon'
import Textarea from 'react-autosize-textarea'

import CheckboxInput from './form/CheckboxInput'
import DateInput from './form/DateInput'
import GeoInput from './form/GeoInput'
import HiddenInput from './form/HiddenInput'
import NumberInput from './form/NumberInput'
import PasswordInput from './form/PasswordInput'
import SelectInput from './form/SelectInput'
import SirenInput from './form/SirenInput'
import TextareaInput from './form/TextareaInput'
import TextInput from './form/TextInput'

const inputByTypes = {
  date: DateInput,
  email: TextInput,
  geo: GeoInput,
  hidden: HiddenInput,
  password: PasswordInput,
  siren: SirenInput,
  siret: SirenInput,
  checkbox: CheckboxInput,
  text: TextInput,
}

class Field extends Component {

  constructor(props) {
    super(props)
    this.state = {
      value: '',
    }
  }

  static defaultProps = {
    layout: 'horizontal',
    size: 'normal',
    displayValue: v => (v || ''),
    storeValue: v => v,
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

  static getDerivedStateFromProps({autoComplete, name, type, required, readonly, value}) {
    type = type || Field.guessInputType(name) // Would be cleaner to use `this` instead of `Field` but doesn't work :(
    const InputComponent = inputByTypes[type]

    if (!InputComponent) console.error('Component not found', this.props.name, type)

    return {
      required: required && !readonly,
      type,
      autoComplete: autoComplete || Field.guessAutoComplete(name, type),
      value,
      InputComponent,
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
    if (value === this.props.value) return

    const displayValue = this.state.InputComponent.displayValue || this.props.displayValue
    const storeValue = this.state.InputComponent.storeValue || this.props.storeValue

    console.log(this.props.name, value)

    this.setState({
      value: displayValue(value),
    }, () => {
      this.props.onChange(this.props.name, storeValue(value))
    })
  }

  renderInput = () => {
    const {
      autoComplete,
      required,
      type,
      value,
      InputComponent,
    } = this.state

    const inputProps = Object.assign({}, this.props, {
      'aria-describedby': `${this.props.id}-error`,
      autoComplete,
      onChange: this.onChange,
      required,
      type,
      value,
    })

    return <InputComponent {...inputProps} className={`input is-${this.props.size}`} />
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
