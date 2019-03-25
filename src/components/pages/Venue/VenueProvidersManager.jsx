import classnames from 'classnames'
import get from 'lodash.get'
import { Field, Form, Icon, mergeForm, SubmitButton } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'
import { selectCurrentUser } from 'with-login'

import VenueProviderItem from './VenueProviderItem'
import selectProviderById from 'selectors/selectProviderById'
import selectProviders from 'selectors/selectProviders'
import selectVenueProviderByVenueIdAndVenueProviderId from 'selectors/selectVenueProviderByVenueIdAndVenueProviderId'
import selectVenueProvidersByVenueId from 'selectors/selectVenueProvidersByVenueId'

class ProviderManager extends Component {
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
            <VenueProviderItem venue={venue} venueProvider={vp} key={vp.id} />
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

function mapStateToProps(state, ownProps) {
  const { venue } = ownProps
  const { id: venueId } = venue || {}
  const providers = selectProviders(state)

  const formPatch = get(state, 'form.venueProvider')

  let provider
  if (providers.length === 1) {
    provider = providers[0]
  } else {
    const providerId = get(formPatch, 'providerId')
    provider = selectProviderById(state, providerId)
  }

  return {
    currentUser: selectCurrentUser(state),
    provider,
    providers,
    venueProvider: selectVenueProviderByVenueIdAndVenueProviderId(
      state,
      venueId
    ),
    venueProviders: selectVenueProvidersByVenueId(state, venueId),
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(ProviderManager)
