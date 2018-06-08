import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import FormField from './layout/FormField'
import Label from './layout/Label'
import SubmitButton from './layout/SubmitButton'
import ProviderItem from './ProviderItem'
import { requestData } from '../reducers/data'
import { mergeForm } from '../reducers/form'
import selectProviderOptions from '../selectors/providerTypeOptions'
import selectProviders from '../selectors/providers'
import selectCurrentVenue from '../selectors/currentVenue'
import { NEW } from '../utils/config'

class ProviderManager extends Component {

  constructor () {
    super()
    this.state = {
      isNew: false,
      withError: false
    }
  }

  onAddClick = () => {
    this.setState({ isNew: true })
  }

  onConfirmClick = e => {
    const {
      mergeForm,
      newProvider,
      providers
    } = this.props

    // build the datetime based on the date plus the time
    // given in the horaire form field
    if (!newProvider || !newProvider.type || !newProvider.identifier) {
      return this.setState({ withError: true })
    }

    // check that it does not match already an occurence
    const alreadySelectedProvider = providers.find(p =>
      p.identifier === newProvider.identifier)
    console.log('alreadySelectedProvider', alreadySelectedProvider)
    if (alreadySelectedProvider) {
      return this.setState({ withError: true })
    }

    // add in the providers form
    const providerId = !providers
      ? `NEW_0`
      : `${NEW}_${providers.length}`
    mergeForm(
      'providers',
      providerId,
      Object.assign({ id: providerId }, newProvider)
    )
  }

  componentDidMount () {
    this.props.requestData('GET', 'providerTypes')
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      match: { params: { providerId } }
    } = nextProps
    const isNew = providerId === 'nouveau'
    return {
      isNew
    }
  }

  render () {
    const {
      providers,
      providerTypeOptions,
      venueProviders
    } = this.props
    const {
      isNew,
      withError
    } = this.state
    // https://openagenda.com/agendas/49050769/events.json
    return [
      <h2 className='subtitle is-2' key={0}>
        Mes fournisseurs
      </h2>,
      <button className="button is-primary level-item"
        onClick={this.onAddClick} key={1}>
        Ajouter un fournisseur
      </button>,
      isNew && (
        <div className='box content' key={2}>
          <p className={
            withError
              ? 'has-text-weight-bold has-text-danger'
              : ''
          }>
            Il faut un identifiant ou celui-ci existe déjà
          </p>
          <FormField
            collectionName="newProviders"
            defaultValue={get(providerTypeOptions, '0.value')}
            label={<Label title="La source" />}
            name="type"
            options={providerTypeOptions}
            type="select"
          />
          <FormField
            collectionName="newProviders"
            label={<Label title="Mon identifiant" />}
            name="identifier"
          />
          <button
            className="button"
            onClick={this.onConfirmClick}>
            Ajouter
          </button>
        </div>
      ),
      providers && providers.map((op, index) => (
        <ProviderItem {...op} key={index} />
      ))
    ]
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => Object.assign(
      {
        newProvider: state.form.newProvidersById && state.form.newProvidersById[NEW],
        providerTypeOptions: selectProviderOptions(state),
        providers: selectProviders(state, ownProps)
      },
      selectCurrentVenue(state, ownProps)
    ),
    { mergeForm, requestData }
  )
)(ProviderManager)
