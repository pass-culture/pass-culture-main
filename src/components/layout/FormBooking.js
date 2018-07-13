// import get from 'lodash.get'
// import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormInput from './FormInput'

import { assignErrors, removeErrors } from '../../reducers/errors'
import { getFormEntity, mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'
import {
  // capitalize,
  removeWhitespaces
} from '../../utils/string'

class FormBooking extends Component {
  constructor(props) {
    super(props)
    this.state = {
      localValue: null,
      searching: false,
    }
  }

  onChange = e => {
    // const {sireType} = this.props
    const value = removeWhitespaces(e.target.value)
    if (value.length === 9) {
      this.fetchBookingInfos(value)
    }
  }

  formatValue = v => {
    const value = removeWhitespaces(v)
    return value.substring(0, 9)
  }

  fetchBookingInfos = inputValue => {
    if (!inputValue) {
      return
    }
    inputValue = removeWhitespaces(inputValue)
    // const {
    //   assignErrors,
    //   collectionName,
    //   entityId,
    //   mergeForm,
    //   sireType,
    // } = this.props

    this.setState({
      localValue: inputValue,
      searching: true,
    })

    // requestData()
    /*
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
    */
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
    return (
      <FormInput
        onChange={this.onChange}
        formatValue={this.formatValue}
        storeValue={removeWhitespaces}
        {...this.props}
        type='text'
      />
    )
  }
}

FormBooking.defaultProps = {
  entityId: NEW,
}

FormBooking.propTypes = {
}

export default connect(
  (state, ownProps) => ({
    entity: getFormEntity(state, ownProps)
  }),
  { assignErrors, mergeForm, removeErrors }
)(FormBooking)
