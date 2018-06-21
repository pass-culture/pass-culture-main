import React, {Component} from 'react'

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
  }

  static typeToAutoComplete(type) {
    return type
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
    this.setState({
      value,
    })
    this.props.onChange(this.props.name, value)
  }


  render() {
    const {
      autoComplete,
      id,
      error,
      label,
      onChange,
      placeholder,
      readOnly,
      required,
      type,
      value,
      wrapperClassName,
    } = this.props
    const $input = <input
      autoComplete={autoComplete || this.constructor.typeToAutoComplete(type)}
      className='input'
      id={id}
      onChange={e => this.onChange(e.target.value)}
      type={type}
      required={required}
      readOnly={readOnly}
      placeholder={placeholder}
      value={this.state.value}
    />
    const $error = error ?
    <ul
      id={`${id}-error`}
      className={'help is-danger'}
    >
      <p>
       <Icon svg="picto-warning" alt="Warning" /> {error}
      </p>
    </ul> : null

    const $label = label ? <label htmlFor={id}>{label} :</label> : null

    return (
      <div className={wrapperClassName}>
        {$label}
        {$input}
        {$error}
      </div>
    );
  }
}

export default Field