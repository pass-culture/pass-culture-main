import debounce from 'lodash.debounce'
import get from 'lodash.get'
import { requestData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, {Component} from 'react'
import { connect } from 'react-redux'

import { newMergeForm, newRemoveErrorForm } from '../../reducers/form'
import { recursiveMap } from '../../utils/react'
import { pluralize } from '../../utils/string'

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
import TimeInput from './form/TimeInput'

const inputByTypes = {
  date: DateInput,
  email: TextInput,
  geo: GeoInput,
  hidden: HiddenInput,
  number: NumberInput,
  password: PasswordInput,
  select: SelectInput,
  siren: SirenInput,
  siret: SirenInput,
  checkbox: CheckboxInput,
  text: TextInput,
  textarea: TextareaInput,
  time: TimeInput,
}


class Form extends Component {

  constructor(props) {
    super(props)
    this.state = {
      editedValues: {},
    }
    this.onDebouncedMergeForm = debounce(
      this.onMergeForm,
      props.debounceTimeout
    )
  }

  static defaultProps = {
    TagName: 'form',
    formData: {},
    formErrors: {},
    debounceTimeout: 300,
    formatData: data => data,
  }

  static propTypes = {
    name: PropTypes.string.isRequired,
    action : PropTypes.string.isRequired,
    data: PropTypes.object,
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
      case 'siret':
      case 'siren':
        return 'siren'
      case 'price':
        return 'number'
      default:
        return 'text'
    }
  }

  static getDerivedStateFromProps = (props, prevState) => {
    return {
      method: props.method || get(props, 'data.id') ? 'PATCH' : 'POST',
    }
  }

  onMergeForm = () => {
    this.props.newRemoveErrorForm(this.props.name)
    this.props.newMergeForm(this.props.name, this.state.editedValues)
    this.setState({
      editedValues: {},
    })
  }

  onSubmit = e => {
    e.preventDefault()
    const {
      action,
      formData,
      formatData,
      handleFail,
      handleSuccess,
      name,
      requestData,
      storePath,
    } = this.props

    requestData(
      this.state.method,
      action.replace(/^\//g, ''), {
      body: formatData(formData),
      formName: name,
      handleFail,
      handleSuccess,
      key: storePath, // key is a reserved prop name
      encode: formData instanceof FormData ? 'multipart/form-data' : null,
    })
  }

  childrenWithProps = () => {
    const {
      children,
      formData,
      formErrors,
      data: storeData,
      layout,
      name,
      readOnly,
      size,
    } = this.props
    let requiredFields = []

    return recursiveMap(children, c => {
      if (c.type.displayName === 'Field') {
        if (c.props.required) {
          requiredFields = requiredFields.concat(c)
        }
        const dataKey = c.props.dataKey || c.props.name // name is unique, dataKey may not
        const formValue = get(formData || {}, dataKey)
        const storeValue = get(storeData || {}, dataKey)
        const type = c.props.type || Form.guessInputType(c.props.name) || 'text'
        const InputComponent = inputByTypes[type]
        if (!InputComponent) console.error('Component not found for type:', type)

        const onChange = value => {
          const newEditedValues = typeof value === 'object' ? value : {[dataKey]: value}
          this.setState({
            editedValues: Object.assign(this.state.editedValues, newEditedValues)
          })
          // this.onDebouncedMergeForm() // Not working for now
          this.onMergeForm()
        }

        return React.cloneElement(c, Object.assign({
          id: `${name}-${c.props.name}`,
          onChange,
          value: formValue || storeValue || '',
          errors: [].concat(formErrors).filter(e => get(e, c.props.name)).map(e => get(e, c.props.name)),
          readOnly: c.props.readOnly || readOnly,
          layout,
          size,
          type,
          InputComponent,
        }, get(InputComponent, 'extraFormData', []).reduce((result, k) => Object.assign(result, {[k]: get(formData, k)}), {})))
      } else if (c.type.displayName === 'Submit') {
        return React.cloneElement(c, Object.assign({
          name,
          getDisabled: () => {
            const missingFields = requiredFields.filter(f => !get(formData, `${f.props.name}`))
            return missingFields.length > 0
          },
          getTitle: () => {
            const missingFields = requiredFields.filter(f => !get(formData, `${f.props.name}`))
            if (missingFields.length === 0) return
            return `Champs ${pluralize('non-valide', missingFields.length)} : ${missingFields.map(f => (f.props.label || f.props.title || '').toLowerCase()).join(', ')}`
          }
        }, this.props.TagName !== 'form' ? {
          // If not a real form, need to mimic the submit behavior
          onClick: this.onSubmit,
          type: 'button',
        } : {}))
      }
      return c
    })
  }

  render() {
    const {
      action,
      className,
      name,
      TagName,
    } = this.props
    const {
      method
    } = this.state
    return (
      <TagName
        action={action}
        className={className}
        id={name}
        method={method}
        onSubmit={this.onSubmit}
      >
        {this.childrenWithProps()}
      </TagName>
    )
  }

}

export default connect(
  (state, ownProps) => ({
    formData: get(state, `form.${ownProps.name}.data`),
    formErrors: get(state, `form.${ownProps.name}.errors`),
  }),
  { newMergeForm, newRemoveErrorForm, requestData }
)(Form)
