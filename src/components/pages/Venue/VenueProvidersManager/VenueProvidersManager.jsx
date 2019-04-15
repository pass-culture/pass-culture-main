import classnames from 'classnames'
import get from 'lodash.get'
import { Field, Form, Icon, mergeForm, SubmitButton } from 'pass-culture-shared'
import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import VenueProviderItemContainer from './VenueProviderItem/VenueProviderItemContainer'

class VenueProvidersManager extends Component {
  constructor() {
    super()
    this.state = {
      withError: false,
    }
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      match: {
        params: { venueProviderId },
      },
    } = nextProps
    const isNew = venueProviderId === 'nouveau'
    return {
      isNew,
    }
  }

  onAddClick = () => {
    const {
      history,
      match: {
        params: { offererId, venueId },
      },
    } = this.props
    history.push(
      `/structures/${offererId}/lieux/${venueId}/fournisseurs/nouveau`
    )
  }

  handleMergeForm = () => {
    const {
      dispatch,
      match: {
        params: { venueId },
      },
    } = this.props
    const { isNew } = this.state
    isNew && dispatch(mergeForm('venueProviders', 'nouveau', { venueId }))
  }

  handleDataRequest = () => {
    const {
      dispatch,
      match: {
        params: { venueId },
      },
    } = this.props
    dispatch(requestData({ apiPath: '/providers' }))
    dispatch(
      requestData({
        apiPath: `/venueProviders?venueId=${venueId}`,
        stateKey: 'venueProviders',
      })
    )
  }

  handleSuccess = () => {
    const {
      history,
      match: {
        params: { offererId, venueId },
      },
    } = this.props
    history.push(`/structures/${offererId}/lieux/${venueId}`)
  }

  componentDidMount() {
    const {
      match: {
        params: { venueProviderId },
      },
    } = this.props
    this.handleDataRequest()
    venueProviderId === 'nouveau' && this.handleMergeForm()
  }

  componentDidUpdate(prevProps) {
    if (
      prevProps.match.params.venueProviderId === 'nouveau' ||
      this.props.match.params.venueProviderId !== 'nouveau'
    ) {
      this.handleMergeForm()
    }
  }

  render() {
    const {
      match: {
        params: { offererId, venueId },
      },
      provider,
      providers,
      venue,
      venueProvider,
      venueProviders,
    } = this.props
    const { identifierDescription, identifierRegexp } = provider || {}
    const { isNew, withError } = this.state

    return (
      <div className="venue-providers-manager section">
        <h2 className="main-list-title">
          IMPORTATIONS D'OFFRES
          <span className="is-pulled-right is-size-7 has-text-grey">
            Si vous avez plusieurs comptes auprès de la même source, ajoutez-les
            successivement.
          </span>
        </h2>
        <ul
          className={classnames('main-list', {
            'is-marginless': !get(venueProviders, 'lenght') && !isNew,
          })}>
          {venueProviders.map((vp, index) => (
            <VenueProviderItemContainer
              venue={venue}
              venueProvider={vp}
              key={vp.id}
            />
          ))}
          {isNew && (
            <li>
              <Form
                action="/venueProviders"
                className="level"
                handleSuccess={this.handleSuccess}
                name="venueProvider"
                patch={venueProvider}>
                <Field type="hidden" name="venueId" />
                {withError && (
                  <p
                    className={
                      withError ? 'has-text-weight-bold has-text-danger' : ''
                    }>
                    Il faut un identifiant ou celui-ci existe déjà
                  </p>
                )}
                <div className="level-left">
                  <div className="field picto level-item">
                    <Icon svg="picto-db-default" />
                  </div>
                  <Field
                    name="providerId"
                    options={providers}
                    optionValue="id"
                    placeholder="Source d\'importation"
                    required
                    size="small"
                    type="select"
                  />
                  {provider && identifierRegexp && (
                    <Field
                      name="venueIdAtOfferProvider"
                      placeholder="identifiant"
                      required
                      size="small"
                      title={identifierDescription}
                    />
                  )}
                </div>
                <div className="field level-item level-right">
                  <NavLink
                    className="button is-secondary"
                    to={`/structures/${offererId}/lieux/${venueId}`}>
                    Annuler
                  </NavLink>
                </div>
                {provider && (
                  <div className="field level-item level-right">
                    <SubmitButton className="button is-secondary">
                      Importer
                    </SubmitButton>
                  </div>
                )}
                <div />
              </Form>
            </li>
          )}
        </ul>
        <div className="has-text-centered">
          <button
            className="button is-secondary"
            disabled={isNew}
            onClick={this.onAddClick}>
            + Importer des offres
          </button>
        </div>
      </div>
    )
  }
}

export default VenueProvidersManager
