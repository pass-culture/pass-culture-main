import React, {Component} from 'react'
import { connect } from 'react-redux'
import debounce from 'lodash.debounce'
import get from 'lodash.get'
import set from 'lodash.set'

import { newMergeForm } from '../../reducers/form'
import { removeErrors } from '../../reducers/errors'

import { recursiveMap } from '../../utils/react'
import { pluralize } from '../../utils/string'

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
    formData: {},
    formErrors: {},
    debounceTimeout: 500,
  }

  static getDerivedStateFromProps = (props, prevState) => {
    return {
      method: props.method || get(props, 'storeData.id') ? 'PATCH' : 'PUT',
    }
  }

  onMergeForm = () => {
    this.props.removeErrors()
    this.props.newMergeForm(this.props.name, this.state.editedValues)
    this.setState({
      editedValues: {},
    })
  }

  onSubmit = e => {
    e.preventDefault()
    const {
      action,
      handleFail,
      handleSuccess,
    } = this.props

    console.log('should submit')
    // TODO: plug this
    // requestData(this.state.method, action, {
    //   add,
    //   body,
    //   getOptimistState,
    //   getSuccessState,
    //   handleFail,
    //   handleSuccess,
    //   key: storeKey,
    //   requestId: submitRequestId,
    //   encode: body instanceof FormData ? 'multipart/form-data' : null,
    // })
  }

  updateFormValue = (key, value) => {
    this.setState({
      editedValues: Object.assign(this.state.editedValues, {[key]: value})
    }, () => {
      this.onDebouncedMergeForm()
    })
  }

  childrenWithProps = () => {
    const {
      action,
      children,
      formData,
      formErrors,
      data: storeData,
      method,
      name,
      readOnly,
    } = this.props
    let requiredFields = []

    return recursiveMap(children, c => {
      if (c.type.displayName === 'Field') {
        if (c.props.required) {
          requiredFields = requiredFields.concat(c)
        }
        const formValue = get(formData || {}, c.props.name)
        const storeValue = get(storeData || {}, c.props.name)
        return React.cloneElement(c, {
          id: `${name}-${c.props.name}`,
          onChange: this.updateFormValue,
          value: (typeof formValue === 'string') ? formValue : storeValue || '',
          error: get(formErrors || {}, c.props.name),
          readOnly: c.props.readOnly || readOnly,
        })
      } else if (c.type.displayName === 'Submit') {
        return React.cloneElement(c, {
          name,
          isDisabled: () => {
            const missingFields = requiredFields.filter(f => !get(formData, `${f.props.name}`))
            return missingFields.length > 0
          },
          getTitle: () => {
            const missingFields = requiredFields.filter(f => !get(formData, `${f.props.name}`))
            if (missingFields.length === 0) return
            return `Champs ${pluralize('non-valide', missingFields.length)} : ${missingFields.map(f => f.props.label.toLowerCase()).join(', ')}`
          }
        })
      }
      return c
    })
  }

  render() {
    const {
      action,
      data: storeData,
      name,
    } = this.props
    const {
      method
    } = this.state
    return (
      <form id={name} method={method} action={action} onSubmit={this.onSubmit}>
        {this.childrenWithProps()}
      </form>
    )
  }

}

export default connect(
  (state, ownProps) => ({
    formData: get(state, `form.${ownProps.name}.data`),
    formErrors: get(state, `form.${ownProps.name}.errors`),
  }),
  { newMergeForm, removeErrors }
)(Form)