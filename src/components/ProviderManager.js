import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import FormField from './layout/FormField'
import Label from './layout/Label'
import Icon from './layout/Icon'
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
    const {
      match: { params: { venueProviderId } },
      user
    } = this.props
    user && this.handleRequestData()
    venueProviderId === 'nouveau' && this.handleMergeForm()
  }

  componentDidUpdate (prevProps) {
    if (prevProps.user !== this.props.user) {
      this.handleRequestData()
    }
    if (
      prevProps.match.params.venueProviderId === 'nouveau'
      || this.props.match.params.venueProviderId !== 'nouveau'
    ) {
      this.handleMergeForm()
    }
  }

  handleMergeForm = () => {
    const {
      match: { params: { venueId } },
      mergeForm
    } = this.props
    mergeForm('venueProviders', NEW, { venueId })
  }

  handleRequestData = () => {
    const {
      match: { params : { venueId } },
      requestData
    } = this.props
    requestData('GET', 'providers')
    requestData(
      'GET',
      `venueProviders?venueId=${venueId}`,
      {
        key: 'venueProviders'
      }
    )
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      match: { params: { venueProviderId } }
    } = nextProps
    const newState = {}
    if (venueProviderId === 'nouveau') {
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

    console.log('providerOptions', providerOptions)
    console.log('venueProviders', venueProviders)
    return (
      <div className='section'>
        <h2 className='pc-list-title'>
          Mes fournisseurs
        </h2>
        <ul className='pc-list'>
          {
            venueProviders && venueProviders.map((vp, index) => (
                <VenueProviderItem {...vp} key={index} />
            ))
          }
          {isNew && (
            <li>
              {withError && (
                <p className={
                  withError ? 'has-text-weight-bold has-text-danger' : ''
                }>Il faut un identifiant ou celui-ci existe déjà</p>
              )}

              <div className='picto'><Icon svg='picto-db-default' /></div>
              <FormField
                collectionName="venueProviders"
                defaultValue={get(providerOptions, '0.value')}
                name="providerId"
                options={providerOptions}
                required
                type="select"
                size="small"
              />
              <FormField
                collectionName="venueProviders"
                name="venueIdAtOfferProvider"
                placeholder='Mon identifiant'
                size="small"
              />
              <SubmitButton
                className="button is-secondary"
                getBody={form => get(form, `venueProvidersById.${NEW}`)}
                getIsDisabled={form =>
                  !get(form, `venueProvidersById.${NEW}.venueIdAtOfferProvider`)}
                handleSuccess={() => this.setState({ isNew: false })}
                method="POST"
                path="venueProviders"
                storeKey="venueProviders"
                text="Enregistrer"
              />
            </li>
          )}
        </ul>
        <div className='has-text-right'>
          <button className="button is-secondary"
            onClick={this.onAddClick}>
            + Ajouter un compte fournisseur
          </button>
        </div>
      </div>
      )
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
