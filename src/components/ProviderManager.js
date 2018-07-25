//import { mergeFormData, requestData } from 'pass-culture-shared'
import { requestData } from 'shared/reducers/data'
import { mergeFormData } from 'shared/reducers/form'

import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import VenueProviderItem from './VenueProviderItem'
import Field from './layout/Field'
import Form from './layout/Form'
import Icon from './layout/Icon'
import SubmitButton from './layout/SubmitButton'
import providerSelector from '../selectors/provider'
import providersSelector from '../selectors/providers'
import venueProvidersSelector from '../selectors/venueProviders'
import { NEW } from '../utils/config'

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
      mergeFormData
    } = this.props
    const { isNew } = this.state
    isNew && mergeFormData('venueProviders', NEW, { venueId })
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
      formData,
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
        <h2 className='pc-list-title'>
          IMPORTATIONS D'OFFRES
          <span className='is-pulled-right is-size-7 has-text-grey'>
            Si vous avez plusieurs comptes auprès de la même source, ajoutez-les successivement.
          </span>
        </h2>
        <ul className='pc-list'>
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
                  data={Object.assign({ venueId: get(venue, 'id') }, formData)}
                  handleSuccess={this.handleSuccess}
                  name='venueProvider'
                >
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
                      type="select"
                    />
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

      let provider
      if (providers.length === 1) {
        provider = providers[0]
      } else {
        const providerId = get(state, `form.venueProvidersById.${NEW}.providerId`)
        provider = providerSelector(state, providerId)
      }

      return {
        formData: get(state, 'form.venueProvider.data'),
        provider,
        providers,
        user: state.user,
        venueProviders: venueProvidersSelector(state, get(ownProps, 'venue.id'))
      }
    },
    { mergeFormData, requestData }
  )
)(ProviderManager)
