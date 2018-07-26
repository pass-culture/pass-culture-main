import get from 'lodash.get'
import {
  Icon,
  Field,
  Form,
  requestData,
  SubmitButton
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'

import ProviderManager from '../ProviderManager'
import PageWrapper from '../layout/PageWrapper'
import { addBlockers, removeBlockers } from '../../reducers/blockers'
import { closeNotification, showNotification } from '../../reducers/notification'
import offererSelector from '../../selectors/offerer'
import venueSelector from '../../selectors/venue'
import { offererNormalizer, venueNormalizer } from '../../utils/normalizers'


class VenuePage extends Component {

  constructor () {
    super()
    this.state = {
      isEdit: false,
      isLoading: false,
      isNew: false,
      isReadOnly: true
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      location: { search },
      match: { params: { offererId, venueId } },
      offerer,
      venue
    } = nextProps
    const isEdit = search === '?modifie'
    const isNew = venueId === 'nouveau'
    const isReadOnly = !isNew && !isEdit
    const offererName = get(offerer, 'name')
    const routePath = `/structures/${offererId}`
    const venueName = get(venue, 'name')
    return {
      apiPath: isNew ? `venues` : `venues/${venueId}`,
      isLoading: !(get(offerer, 'id') && (get(venue, 'id') || isNew)),
      isNew,
      method: isNew ? 'POST' : 'PATCH',
      isEdit,
      isReadOnly,
      offererName,
      routePath,
      venueName
    }
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      match,
      requestData
    } = this.props
    const { apiPath } = this.state
    requestData(
      'GET',
      `offerers/${match.params.offererId}`,
      {
        handleSuccess: () => {
          requestData(
            'GET',
            apiPath,
            {
              handleSuccess,
              handleFail,
              key: 'venues',
              normalizer: venueNormalizer
            }
          )
        },
        handleFail,
        key: 'offerers',
        normalizer: offererNormalizer
      }
    )
  }

  handleSuccess = (state, action) => {
    const {
      addBlockers,
      closeNotification,
      history,
      offerer,
      removeBlockers,
      showNotification
    } = this.props
    const venueId = get(action, 'data.id')
    if (!venueId) {
      console.warn('You should have a venueId here')
      return
    }

    // const redirectPathname = `/structures/${offerer.id}`
    const redirectPathname = get(action, 'method') === 'POST'
      ? `/structures/${get(offerer, 'id')}/lieux/${venueId}`
      : `/structures/${get(offerer, 'id')}`
    history.push(redirectPathname)
    showNotification({
      text: get(action, 'method') === 'POST'
        ? "Lieu ajouté avec succès !"
        : "Lieu modifié avec succès !",
      type: 'success'
    })
    addBlockers(
      'venue-notification',
      ({ location: { pathname }}) => {
        if (pathname === redirectPathname) {
          removeBlockers('venue-notification')
          closeNotification()
        }
      }
    )
  }

  render () {
    const {
      match: {
        params: { offererId }
      },
      location: {
        pathname
      },
      offerer,
      user,
      venue,
    } = this.props

    const {
      offererName,
      isNew,
      isReadOnly,
      routePath,
      venueName
    } = this.state

    return (
      <PageWrapper
        backTo={{
          label: offererName === venueName
            ? 'STRUCTURE'
            : offererName,
          path: routePath
        }}
        name='venue'
        handleDataRequest={this.handleDataRequest}
      >
        <div className='section hero'>
          <h2 className='subtitle has-text-weight-bold'>
            {get(venue, 'name')}
          </h2>

          <h1 className='pc-title'>
            Lieu
          </h1>

          {
            isNew && (
              <p className="subtitle">
                Ajoutez un lieu où accéder à vos offres.
              </p>
            )
          }

          {
            get(offerer, 'id') && get(venue, 'id') && (
              <NavLink to={`/offres/nouveau?lieu=${venue.id}`}
                className='button is-primary is-medium is-pulled-right cta'>
                <span className='icon'><Icon svg='ico-offres-w' /></span>
                <span>Créer une offre</span>
              </NavLink>
            )
          }
        </div>

        {!isNew && <ProviderManager venue={venue} />}

        <Form
          action={`/venues/${get(venue, 'id', '')}`}
          handleSuccess={this.handleSuccess}
          name='venue'
          patch={Object.assign({}, venue, {
            managingOffererId: offererId,
            bookingEmail: get(user, 'email')
          })}
          readOnly={isReadOnly}
        >
          <Field type='hidden' name='managingOffererId' />
          <div className='section'>
            <h2 className='pc-list-title'>
              IDENTIFIANTS
              <span className='is-pulled-right is-size-7 has-text-grey'>
                Les champs marqués d'un <span className='required-legend'> * </span> sont obligatoires
              </span>
            </h2>
            <div className='field-group'>
              <Field label='SIRET' name='siret' type='siret' />
              <Field label='Nom du lieu' name='name' required />
              <Field label='E-mail' name='bookingEmail' required type='email' />
            </div>
          </div>
          <div className='section'>
            <h2 className='pc-list-title'>
              ADRESSE
            </h2>
            <div className='field-group'>
              <Field
                isExpanded
                label='Numéro et voie'
                name='address'
                required
                type="geo"
                withMap />
              <Field
                autocomplete='postal-code'
                label='Code postal'
                name='postalCode'
                required />
              <Field
                autocomplete='address-level2'
                label='Ville'
                name='city'
                required />
              <Field
                label='Longitude'
                name='longitude'
                required />
              <Field
                label='Latitude'
                name='latitude'
                required />
            </div>
          </div>
        <hr />
        <div className="field is-grouped is-grouped-centered"
          style={{justifyContent: 'space-between'}}>
          <div className="control">
            {
              isReadOnly
                ? (
                  <NavLink
                    className='button is-secondary is-medium'
                    to={`${pathname}?modifie`} >
                    Modifier le lieu
                  </NavLink>
                )
                : (
                  <NavLink
                    className="button is-secondary is-medium"
                    to={`/structures/${offererId}`}>
                    Annuler
                  </NavLink>
                )
            }
          </div>
          <div className="control">
            <div className="field is-grouped is-grouped-centered"
              style={{justifyContent: 'space-between'}}>
              <div className="control">
                {
                  isReadOnly
                    ? (
                      <NavLink
                        className='button is-primary is-medium'
                        to={routePath} >
                        Terminer
                      </NavLink>
                    )
                    : (
                      <SubmitButton className="button is-primary is-medium">
                        {isNew ? 'Créer' : 'Valider'}
                      </SubmitButton>
                    )
                }
              </div>
            </div>
          </div>
        </div>
      </Form>
    </PageWrapper>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({
      user: state.user,
      venue: venueSelector(state, ownProps.match.params.venueId),
      offerer: offererSelector(state, ownProps.match.params.offererId),
    }),
    {
      addBlockers,
      closeNotification,
      removeBlockers,
      requestData,
      showNotification
    })
)(VenuePage)
