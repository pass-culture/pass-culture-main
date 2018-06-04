import debounce from 'lodash.debounce'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { assignErrors, removeErrors } from '../../reducers/errors'
import { getFormValue, mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'

class FormSirene extends Component {
  constructor(props) {
    super(props)
    this.state = { localValue: null }
    this.onDebouncedMergeForm = debounce(
      this.onMergeForm,
      props.debounceTimeout
    )
  }

  onChange = event => {
    event.persist()
    this.onDebouncedMergeForm(event)
    this.setState({ localValue: event.target.value })
  }

  onConfirmClick = event => {
    const {
      assignErrors,
      collectionName,
      entityId,
      mergeForm
    } = this.props

    if (!this.state.localValue) {
      return
    }
    const siretWithoutSpaces = this.state.localValue.replace(/ /g, '')

      fetch(`https://sirene.entreprise.api.gouv.fr/v1/siret/${siretWithoutSpaces}`).then(response => {
        if (response.status === 404)  {
          assignErrors('siret', ['Siret invalide'])
          this.setState({localValue: ''})
          mergeForm(collectionName, entityId, 'siret', null)

      } else {
        response.json().then(body => {
          const name = body.etablissement.l1_declaree
          const address = body.etablissement.geo_adresse
          const latitude = body.etablissement.latitude
          const longitude = body.etablissement.longitude
          mergeForm('venues', entityId, { address, latitude, longitude, name })
        }
      )
      }
    }).catch((e) => {
      console.log('erreur', e);
    }

    )

  }

  onMergeForm = event => {
    const {
      target: { value },
    } = event
    const {
      collectionName,
      entityId,
      mergeForm,
      name,
      removeErrors,
    } = this.props
    removeErrors(name)
    mergeForm(collectionName, entityId, name, value)
  }

  componentWillMount() {
    // fill automatically the form when it is a NEW POST action
    const { defaultValue, entityId } = this.props
    defaultValue &&
      entityId === NEW &&
      this.onMergeForm({ target: { value: defaultValue } })
  }

  render() {
    const {
      className,
      defaultValue,
      id,
      placeholder,
      autoComplete,
      type,
      value,
    } = this.props
    const { localValue } = this.state
    return [
      <input
        key='0'
        autoComplete={autoComplete}
        className={className || 'input'}
        id={id}
        onChange={this.onChange}
        placeholder={placeholder}
        type={type}
        value={localValue !== null ? localValue : value || defaultValue || ''}
      />,
      <button key='1' className='button' onClick={this.onConfirmClick}/>
    ]
  }
}

FormSirene.defaultProps = {
  debounceTimeout: 500,
  entityId: NEW,
}

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { assignErrors, mergeForm, removeErrors }
)(FormSirene)
