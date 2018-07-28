import get from 'lodash.get'
import {
  Field,
  Form,
  Icon,
  mergeForm,
  requestData,
  SubmitButton
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import VenueProviderItem from './VenueProviderItem'
import providerSelector from '../selectors/provider'
import providersSelector from '../selectors/providers'
import venueProvidersSelector from '../selectors/venueProviders'

class ProviderManager extends Component {

  constructor () {
    super()
    this.state = {
      withError: false
    }
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      match: { params: { venueProviderId } }
    } = nextProps
    const isNew = venueProviderId === 'nouveau'
    return {
      isNew
    }
  }

  onAddClick = () => {
    const {
      history,
      match: { params: { offererId, venueId } }
    } = this.props
    history.push(`/structures/${offererId}/lieux/${venueId}/fournisseurs/nouveau`)
  }

  handleMergeForm = () => {
    const {
      match: { params: { venueId } },
      mergeForm
    } = this.props
    const { isNew } = this.state
    isNew && mergeForm('venueProviders', 'nouveau', { venueId })
  }

  handleDataRequest = () => {
    const {
      match: { params : { venueId } },
      requestData,
      user
    } = this.props
    if (!user) {
      return
    }
    requestData('GET', 'providers')
    requestData(
      'GET',
      `venueProviders?venueId=${venueId}`,
      {
        key: 'venueProviders',
      }
    )
  }

  handleSuccess = () => {
    const {
      history,
      match: { params: { offererId, venueId } }
    } = this.props
    history.push(`/structures/${offererId}/lieux/${venueId}`)
  }

  componentDidMount () {
    const {
      match: { params: { venueProviderId } },
    } = this.props
    this.handleDataRequest()
    venueProviderId === 'nouveau' && this.handleMergeForm()
  }

  componentDidUpdate (prevProps) {
    if (prevProps.user !== this.props.user) {
      this.handleDataRequest()
    }
    if (
      prevProps.match.params.venueProviderId === 'nouveau'
      || this.props.match.params.venueProviderId !== 'nouveau'
    ) {
      this.handleMergeForm()
    }
  }

  render () {
    const {
      formPatch,
      match: { params: { offererId, venueId } },
      provider,
      providers,
      venue,
      venueProviders
    } = this.props
    const {
      identifierDescription,
      identifierRegexp,
    } = (provider || {})
    const {
      isNew,
      withError
    } = this.state

    return (
      <div className='provider-manager section'>
        <h2 className='main-list-title'>
          IMPORTATIONS D'OFFRES
          <span className='is-pulled-right is-size-7 has-text-grey'>
            Si vous avez plusieurs comptes auprès de la même source, ajoutez-les successivement.
          </span>
        </h2>
        <ul className='main-list'>
          {
            venueProviders.map((vp, index) => (
                <VenueProviderItem
                  venue={venue}
                  venueProvider={vp}
                  key={vp.id}
                />
            ))
          }
          {
            isNew && (
              <li>
                <Form
                  action='/venueProviders'
                  className='level'
                  handleSuccess={this.handleSuccess}
                  name='venueProvider'
                  patch={Object.assign({ venueId: get(venue, 'id') }, formPatch)}>
                  <Field type='hidden' name='venueId' />
                  {
                    withError && (
                      <p className={
                        withError ? 'has-text-weight-bold has-text-danger' : ''
                      }>
                        Il faut un identifiant ou celui-ci existe déjà
                      </p>
                    )
                  }
                  <div className='level-left'>
                    <div className='field picto level-item'>
                      <Icon svg='picto-db-default' />
                    </div>
                    <Field
                      name='providerId'
                      options={providers}
                      optionValue='id'
                      placeholder="Source d\'importation"
                      required
                      size="small"
                      type="select" />
                    {
                      provider && identifierRegexp && (
                        <Field
                          name="venueIdAtOfferProvider"
                          placeholder="identifiant"
                          required
                          size="small"
                          title={identifierDescription}
                        />
                      )
                    }
                  </div>
                  <div className='field level-item level-right'>
                    <NavLink
                      className='button is-secondary'
                      to={`/structures/${offererId}/lieux/${venueId}`} >
                      Annuler
                    </NavLink>
                  </div>
                  {
                    provider && (
                      <div className='field level-item level-right'>
                        <SubmitButton className="button is-secondary">
                          Importer
                        </SubmitButton>
                      </div>
                    )
                  }
                  <div />
                </Form>
              </li>
            )
          }
        </ul>
        <div className='has-text-centered'>
          <button className="button is-secondary"
            disabled={isNew}
            onClick={this.onAddClick}>
            + Importer des offres
          </button>
        </div>
      </div>
      )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const providers = providersSelector(state)

      const formPatch = get(state, 'form.venueProvider.data')

      let provider
      if (providers.length === 1) {
        provider = providers[0]
      } else {
        const providerId = get(formPatch, 'providerId')
        provider = providerSelector(state, providerId)
      }

      return {
        formPatch,
        provider,
        providers,
        user: state.user,
        venueProviders: venueProvidersSelector(state, get(ownProps, 'venue.id'))
      }
    },
    { mergeForm, requestData }
  )
)(ProviderManager)
