import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

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
    const {
      collectionName,
      entityId,
      mergeForm,
      sireType
    } = this.props
    const value = removeWhitespaces(e.target.value)
    if (sireType === SIREN && value.length === 9) {
      this.fetchEntrepriseInfos(value)
    } else if (sireType === SIRET && value.length === 14) {
      this.fetchEntrepriseInfos(value)
    } else if (value.length > 0) {
      mergeForm(collectionName, entityId, 'name', null)
    }
  }

  formatValue = v => {
    const value = removeWhitespaces(v)
    if (!value) {
      return ''
    }
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
          mergeForm(collectionName, entityId,
            {
              address: null,
              city: null,
              latitude: null,
              longitude: null,
              name: null,
              postalCode: null,
              [sireType]: null
            }
          )

        } else {
          response.json().then(body => {
            const dataPath = isSiren ? 'siege_social' : 'etablissement'
            const name =  get(body, `${dataPath}.l1_normalisee`) ||  get(body, `${dataPath}.l1_declaree`) || ''
            const sireneForm = {
              address: get(body, `${dataPath}.geo_adresse`),
              city: get(body, `${dataPath}.libelle_commune`),
              latitude: get(body, `${dataPath}.latitude`),
              longitude: get(body, `${dataPath}.longitude`),
              name: name,
              postalCode: get(body, `${dataPath}.code_postal`),
              [sireType]: get(body, `${dataPath}${sireType}`),
            }
            mergeForm(collectionName, entityId, sireneForm)
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
    const input =
        <FormInput
          onChange={this.onChange}
          formatValue={this.formatValue}
          storeValue={removeWhitespaces}
          {...this.props}
          type='text'
        />
    if (this.props.withDisplayName) {
      return <div className='with-display-name'>
        {input}
        <div className='display-name'>{get(this.props, 'entity.name')}</div>
      </div>
    }
    return input
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
