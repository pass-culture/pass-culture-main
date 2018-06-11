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
    const {
      match: { params: { venueId } },
      mergeForm
    } = this.props
    this.setState({ isNew: true })
    mergeForm('venueProviders', NEW, { venueId })
  }

  componentDidMount () {
    this.props.user && this.handleRequestData()
  }

  componentDidUpdate (prevProps) {
    if (prevProps.user !== this.props.user) {
      this.handleRequestData()
    }
  }

  handleRequestData = () => {
    const {
      match: { params : { venueId } },
      requestData
    } = this.props
    requestData('GET', 'providers')
    requestData(
      'GET',
      `venueProviders/${venueId}`,
      {
        key: 'venueProviders',
        isMergingArray: false
      }
    )
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      match: { params: { providerId } }
    } = nextProps
    const newState = {}
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
            collectionName="venueProviders"
            defaultValue={get(providerOptions, '0.value')}
            label={<Label title="La source" />}
            name="providerId"
            options={providerOptions}
            type="select"
          />
          <FormField
            collectionName="venueProviders"
            label={<Label title="Mon identifiant" />}
            name="venueIdAtOfferProvider"
          />
          <SubmitButton
            className="button is-primary is-medium"
            getBody={form => get(form, `venueProvidersById.${NEW}`)}
            getIsDisabled={form =>
              !get(form, `venueProvidersById.${NEW}.venueIdAtOfferProvider`)}
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
      providerOptions: selectProviderOptions(state),
      providers: state.data.providers,
      venueProviders: selectVenueProviders(state, ownProps),
      venue: selectCurrentVenue(state, ownProps),
      user: state.user
    }),
    { mergeForm, requestData }
  )
)(ProviderManager)
