import debounce from 'lodash.debounce'
import PropTypes from 'prop-types'
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
      mergeForm,
      sireType,
    } = this.props

    if (!this.state.localValue) {
      return
    }

    if (sireType === 'siret') {
      const siretWithoutSpaces = this.state.localValue.replace(/\s/g, '')

      fetch(`https://sirene.entreprise.api.gouv.fr/v1/siret/${siretWithoutSpaces}`).then(response => {
        if (response.status === 404)  {
          assignErrors({siret: ['Siret invalide']})
          this.setState({localValue: ''})
          mergeForm(collectionName, entityId, 'siret', null)

        } else {
          response.json().then(body => {
            const name = body.etablissement.l1_declaree
            const address = body.etablissement.geo_adresse
            const latitude = body.etablissement.latitude
            const longitude = body.etablissement.longitude
            const siret = body.etablissement.siret
            const departementCode = body.etablissement.code_postal
            const city = body.etablissement.libelle_commune
            mergeForm('venues', entityId, { address, latitude, longitude, name, siret, departementCode, city })
          }
        )
      }
    }).catch((e) => { console.log('erreur', e)})
  } else if ((sireType === 'siren')) {
    const sirenWithoutSpaces = this.state.localValue.replace(/\s/g, '')

    fetch(`https://sirene.entreprise.api.gouv.fr/v1/siren/${sirenWithoutSpaces}`).then(response => {
      if (response.status === 404)  {
        assignErrors({siren: ['Siren invalide']})
        this.setState({localValue: ''})
        mergeForm(collectionName, entityId, 'siren', null)

      } else {
        response.json().then(body => {
          const name = body.siege_social[0].l1_declaree
          const address = body.siege_social[0].geo_adresse
          const latitude = body.siege_social[0].latitude
          const longitude = body.siege_social[0].longitude
          const siren = body.siege_social[0].siren
          mergeForm('offerers', entityId, { address, latitude, longitude, name, siren })
        }
      )
    }
  }).catch((e) => { console.log('erreur', e)})
}
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

FormSirene.propTypes = {
  sireType: PropTypes.string.isRequired,
}

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { assignErrors, mergeForm, removeErrors }
)(FormSirene)
