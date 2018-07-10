import React, {Component} from 'react'
import classnames from 'classnames'
import { removeWhitespaces, formatSiren } from '../../utils/string'
import Icon from './Icon'

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
  }

  static nameToInputType(name) {
    switch(name) {
      case 'siren':
        return 'text'
      default:
        return 'text'
    }

  }

  static nameToAutoComplete(name) {
    switch(name) {
      default:
        return name
    }
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
          displayValue: v => v,
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

  renderLayout = ($input, $label, error) => {
    const {
      layout,
      required,
    } = this.props
    switch(layout) {
      case 'horizontal':
        return <div className={`field is-horizontal ${classnames({required})}`}>
          <div className='field-label'>{$label}</div>
          <div className='field-body'>{$input}</div>
          {error && <p className='help is-danger'>
            <Icon svg="picto-warning" alt="Warning" /> {error}
          </p>}
        </div>
      default:
        return $input
    }
    return $input
  }

  render() {
    const {
      autoComplete,
      id,
      error,
      label,
      name,
      onChange,
      placeholder,
      readOnly,
      required,
      type,
      value,
      wrapperClassName,
    } = this.props
    const $input = <input
      autoComplete={autoComplete || this.constructor.nameToAutoComplete(name)}
      className='input'
      id={id}
      onChange={e => this.onChange(e.target.value)}
      type={type || this.constructor.nameToInputType(name)}
      required={required}
      readOnly={readOnly}
      placeholder={placeholder}
      value={this.state.value}
    />

    const $label = label ? <label htmlFor={id}>{label} :</label> : null

    return this.renderLayout($input, $label, error)
  }
}

export default Field