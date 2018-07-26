import classnames from 'classnames'
import { Icon } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component } from 'react'


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

  componentDidMount() {
    this.props.value && this.onChange(this.props.value)
  }

  componentDidUpdate(prevProps) {
    if (
      prevProps.value !== this.props.value ||
      prevProps.readOnly && !this.props.readOnly
    ) {
      this.onChange(this.props.value)
    }
  }

  onChange = (value) => {

    const displayValue = this.props.InputComponent.displayValue ||
      this.props.displayValue
    const storeValue = this.props.InputComponent.storeValue ||
      this.props.storeValue

    this.setState({ value: displayValue(value, this.props) })

    this.props.onChange(storeValue(value, this.props))
  }

  renderInput = () => {

    const inputProps = Object.assign({}, this.props, {
      'aria-describedby': `${this.props.id}-error`,
      onChange: this.onChange,
      required: this.props.required && !this.props.readonly,
      value: this.state.value,
    })

    const InputComponent = this.props.InputComponent

    return <InputComponent {...inputProps} />
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
      type,
    } = this.props
    const $input = this.renderInput()

    if (type === 'hidden') return $input
    switch(layout) {
      case 'horizontal':
        return (
          <div className='field is-horizontal'>
            {
              label && (
                <div className={`field-label is-${size}`}>
                  <label htmlFor={id} className='label'>
                    <span className={`subtitle ${classnames({required, readOnly})}`}>
                      {label} :
                    </span>
                  </label>
                </div>
              )
            }
            <div className='field-body'>
              <div className={`field ${classnames({'is-expanded': isExpanded})}`}>
                {$input}
              </div>
              {
                errors && errors.map((e, i) => (
                  <p className='help is-danger columns' id={`${id}-error`} key={i}>
                    <Icon className='column is-1' svg="picto-warning" alt="Warning" />
                    <span className='column'> {e} </span>
                  </p>
                ))
              }
            </div>
          </div>
        )
      case 'sign-in-up':
        if (type === 'checkbox') {
          return <div className='field checkbox'>{$input}</div>
        } else {
          const {sublabel} = this.props
          return (
            <div className="field">
              {
                label && (
                  <label className='label' htmlFor={id}>
                    <h3 className={classnames({required, 'with-subtitle': sublabel})}>
                      {label}
                    </h3>
                    {sublabel && <p>... {sublabel} :</p>}
                  </label>
                )
              }
            <div className="control">
              {$input}
            </div>
            <ul className="help is-danger" id={`${id}-error`}>
              {
                errors && errors.map((e, i) => (
                  <li className="columns" key={i}>
                    <Icon className="column is-1" svg="picto-warning" alt="Warning" />
                    <p className="column"> {e} </p>
                  </li>
                ))
              }
            </ul>
          </div>
        )}
      default:
        break
    }
    return $input
  }

  render() {
    return this.renderLayout()
  }
}

// NEEDED FOR MINIFY BUILD TIME
// BECAUCE c.type.displayName DISAPPEAR OTHERWISE
Field.displayName = "Field"

export default Field
