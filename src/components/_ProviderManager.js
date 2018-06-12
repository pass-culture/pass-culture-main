import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import FormField from './layout/FormField'
import Label from './layout/Label'
import SubmitButton from './layout/SubmitButton'
import VenueProviderItem from './VenueProviderItem'
import { requestData } from '../reducers/data'
import { mergeForm } from '../reducers/form'
import selectCurrentVenue from '../selectors/currentVenue'
import selectProviderOptions from '../selectors/providerOptions'
import selectVenueProviders from '../selectors/venueProviders'
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

  /*
  onConfirmClick = e => {
    const {
      mergeForm,
      newVenueProvider,
      providers,
      venueProviders
    } = this.props

    // build the datetime based on the date plus the time
    // given in the horaire form field
    if (!newVenueProvider || !newVenueProvider.providerId || !newVenueProvider.identifier) {
      return this.setState({ withError: true })
    }

    // check that it does not match already an occurence
    const alreadySelectedProvider = venueProviders.find(p =>
      p.identifier === newVenueProvider.identifier)
    if (alreadySelectedProvider) {
      return this.setState({ withError: true })
    }

    // find the providers
    const provider = providers.find(p => p.id === newVenueProvider.providerId)

    // add in the venueProviders form
    const venueProviderId = !venueProviders
      ? `NEW_0`
      : `${NEW}_${venueProviders.length}`
    mergeForm(
      'venueProviders',
      venueProviderId,
      Object.assign({
        provider
      }, newVenueProvider)
    )
  }
  */



  componentDidMount () {
    this.props.requestData('GET', 'providers', { key: 'providers' })
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      match: { params: { providerId } }
    } = nextProps
    const method = isNew ? 'POST' : 'PATCH'
    const newState = {
      apiPath: isNew
        ? `venueProviders/`
        : `venueProviders/${venueId}`,
      method
    }
    if (providerId === 'nouveau') {
      newState.isNew = true
    }
    return newState
  }

  render () {
    const {
      providerOptions,
      venueProviders
    } = this.props
    const {
      isNew,
      withError
    } = this.state
    //OA: 9050769
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
            collectionName="newVenueProviders"
            defaultValue={get(providerOptions, '0.value')}
            label={<Label title="La source" />}
            name="providerId"
            options={providerOptions}
            type="select"
          />
          <FormField
            collectionName="newVenueProviders"
            label={<Label title="Mon identifiant" />}
            name="identifier"
          />
          {
            /*
            <button
              className="button"
              onClick={this.onConfirmClick}>
              Ajouter
            </button>
            */
          }
          <SubmitButton
            getBody={}
            getIsDisabled={}
            className="button is-primary is-medium"
            method="POST"
            path="venueProviders"
            storeKey="venueProviders"
            text="Enregistrer"
          />
        </div>
      ),
      venueProviders && venueProviders.map((vp, index) => (
        <VenueProviderItem {...vp} key={index} />
      ))
    ]
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({
      newVenueProvider: state.form.newVenueProvidersById &&
          state.form.newVenueProvidersById[NEW],
      providerOptions: selectProviderOptions(state),
      providers: state.data.providers,
      venueProviders: selectVenueProviders(state, ownProps),
      venue: selectCurrentVenue(state, ownProps)
    }),
    { mergeForm, requestData }
  )
)(ProviderManager)
