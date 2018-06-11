import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'
import FormInput from './FormInput'

import { assignErrors, removeErrors } from '../../reducers/errors'
import { getFormEntity, mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'
import { capitalize, removeWhitespaces } from '../../utils/string'

const SIRET = 'siret'
const SIREN = 'siren'

class FormSirene extends Component {
  constructor(props) {
    super(props)
    this.state = {
      localValue: null,
      searching: false,
    }
  }

  onChange = e => {
    const {sireType} = this.props
    const value = removeWhitespaces(e.target.value)
    if (sireType === SIREN && value.length === 9) {
      this.fetchEntrepriseInfos(value)
    } else if (sireType === SIRET && value.length === 14) {
      this.fetchEntrepriseInfos(value)
    }
  }

  formatValue = v => {
    const value = removeWhitespaces(v)
    const {sireType} = this.props
    const siren = value.substring(0, 9)
    const nic = value.substring(9)
    const formattedSiren = (siren.match(/.{1,3}/g) || []).join(' ')
    if (sireType === SIREN) return formattedSiren
    return `${formattedSiren} ${nic}`
  }

  fetchEntrepriseInfos = inputValue => {
    if (!inputValue) {
      return
    }
    inputValue = removeWhitespaces(inputValue)
    const {
      assignErrors,
      collectionName,
      entityId,
      mergeForm,
      name,
      sireType,
    } = this.props

    const isSiren = sireType === SIREN

    this.setState({
      localValue: inputValue,
      searching: true,
    })
    fetch(`https://sirene.entreprise.api.gouv.fr/v1/${sireType}/${inputValue}`)
      .then(response => {
        this.setState({
          searching: false,
        })
        if (response.status === 404)  {
          assignErrors({[sireType]: [`${capitalize(sireType)} invalide`]})
          this.setState({localValue: ''})
          mergeForm(collectionName, entityId, sireType, null)

        } else {
          response.json().then(body => {
            const dataPath = isSiren ? 'siege_social.0' : 'etablissement'
            mergeForm(collectionName, entityId, {
              address: get(body, `${dataPath}.geo_adresse`),
              latitude: get(body, `${dataPath}.latitude`),
              longitude: get(body, `${dataPath}.longitude`),
              name: get(body, `${dataPath}.l1_declaree`),
              departementCode: get(body, `${dataPath}.code_postal`),
              city: get(body, `${dataPath}.libelle_commune`),
              [sireType]: get(body, `${dataPath}${sireType}`),
            })
          })
        }
      })
      .catch((e) => { console.log('erreur', e)})
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
    } = this.props

    const {name} = this.props.entity || {}
    const { localValue, searching } = this.state

    return [
        <FormInput
          onChange={this.onChange}
          formatValue={this.formatValue}
          key={0}
          storeValue={removeWhitespaces}
          {...this.props}
          type='text'
        />,
        name && (
          <p className="has-text-weight-bold" key={1}>
            {name}
          </p>
        )
      ]
  }
}

FormSirene.defaultProps = {
  entityId: NEW,
}

FormSirene.propTypes = {
  sireType: PropTypes.string.isRequired,
}

export default connect(
  (state, ownProps) => ({ entity: getFormEntity(state, ownProps) }),
  { assignErrors, mergeForm, removeErrors }
)(FormSirene)
