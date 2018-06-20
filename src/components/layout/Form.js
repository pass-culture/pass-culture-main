import React, {Component} from 'react'
import { connect } from 'react-redux'
import debounce from 'lodash.debounce'
import get from 'lodash.get'

import { mergeForm } from '../../reducers/form'
import { removeErrors } from '../../reducers/errors'

import {recursiveMap} from '../../utils/react'

class Form extends Component {

  static defaultProps = {
    formData: {},
    formErrors: {},
    debounceTimeout: 500,
  }

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

  onMergeForm = () => {
    this.props.removeErrors()
    this.props.mergeForm(this.props.name, this.state.editedValues)
    this.setState({
      editedValues: {},
    })
  }

  onSubmit = e => {
    e.preventDefault()
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
    } = this.props
    let requiredFields = []
    return recursiveMap(children, c => {
      if (c.type.displayName === 'Field') {
        if (c.props.required) {
          requiredFields = requiredFields.concat(c.props.name)
        }
        const formValue = get(formData || {}, c.props.name)
        const storeValue = get(storeData || {}, c.props.name)
        return React.cloneElement(c, {
          id: `${name}-${c.props.name}`,
          onChange: this.updateFormValue,
          value: (typeof formValue === 'string') ? formValue : storeValue,
          error: get(formErrors || {}, c.props.name),
        })
      } else if (c.type.displayName === 'Submit') {
        return React.cloneElement(c, {
          name,
          isDisabled: () => {
            const missingFields = requiredFields.filter(f => !get(formData, `${f}`))
            return missingFields.length > 0
          },
        })
      }
      return c
    })
  }

  render() {
    const {
      action,
      data: storeData,
      method,
      name,
    } = this.props
    return (
      <form id={name} method={method || (get(storeData, 'id') ? 'PATCH' : 'POST')} action={action} onSubmit={this.onSubmit}>
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
  { mergeForm, removeErrors }
)(Form)