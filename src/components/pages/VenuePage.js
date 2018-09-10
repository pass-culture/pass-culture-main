import get from 'lodash.get'
import {
  CancelButton,
  Icon,
  Field,
  Form,
  requestData,
  showNotification,
  SubmitButton,
  withLogin,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Main from '../layout/Main'
import ProviderManager from '../managers/ProviderManager'
import offererSelector from '../../selectors/offerer'
import selectVenuePatchByVenueIdByOffererId from '../../selectors/selectVenuePatchByVenueIdByOffererId'
import { offererNormalizer, venueNormalizer } from '../../utils/normalizers'

class VenuePage extends Component {
  constructor() {
    super()
    this.state = {
      isLoading: false,
      isNew: false,
      isReadOnly: true,
    }
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      location: { search },
      match: {
        params: { venueId },
      },
    } = nextProps
    const isEdit = search.includes('modifie')
    const isNew = venueId === 'nouveau'
    const isReadOnly = !isNew && !isEdit
    return {
      isNew,
      isReadOnly,
    }
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      match: {
        params: { offererId, venueId },
      },
      requestData,
      venue,
    } = this.props
    if (!venue && venueId !== 'nouveau') {
      requestData('GET', `offerers/${offererId}`, {
        handleSuccess: () => {
          requestData('GET', `venues/${venueId}`, {
            handleSuccess,
            handleFail,
            key: 'venues',
            normalizer: venueNormalizer,
          })
        },
        handleFail,
        key: 'offerers',
        normalizer: offererNormalizer,
      })
    } else {
      return handleSuccess()
    }
  }

  handleSuccess = (state, action) => {
    const { history, offerer, showNotification } = this.props
    const venueId = get(action, 'data.id')
    if (!venueId) {
      console.warn('You should have a venueId here')
      return
    }

    // const redirectPathname = `/structures/${offerer.id}`
    const redirectPathname =
      get(action, 'method') === 'POST'
        ? `/structures/${get(offerer, 'id')}/lieux/${venueId}`
        : `/structures/${get(offerer, 'id')}`
    history.push(redirectPathname)
    showNotification({
      text:
        get(action, 'method') === 'POST'
          ? 'Lieu ajouté avec succès !'
          : 'Lieu modifié avec succès !',
      type: 'success',
    })
    // TODO: do it in the way that the notification
    // is displayed in the next page an disapeear when
    // the user is after changing to another page
  }

  render() {
    const {
      match: {
        params: { offererId, venueId },
      },
      offerer,
      venuePatch,
    } = this.props

    const { isNew, isReadOnly } = this.state

    return (
      <Main
        backTo={{
          label:
            get(offerer, 'name') === get(venuePatch, 'name')
              ? 'STRUCTURE'
              : get(offerer, 'name'),
          path: `/structures/${offererId}`,
        }}
        name="venue"
        handleDataRequest={this.handleDataRequest}>
        <div className="section hero">
          <h2 className="subtitle has-text-weight-bold">
            {get(venuePatch, 'name')}
          </h2>

          <h1 className="main-title">Lieu</h1>

          {isNew && (
            <p className="subtitle">Ajoutez un lieu où accéder à vos offres.</p>
          )}

          {get(offerer, 'id') &&
            get(venuePatch, 'id') && (
              <NavLink
                to={`/offres/nouveau?lieu=${venuePatch.id}`}
                className="button is-primary is-medium is-pulled-right cta">
                <span className="icon">
                  <Icon svg="ico-offres-w" />
                </span>
                <span>Créer une offre</span>
              </NavLink>
            )}
        </div>

        {!isNew && <ProviderManager venue={venuePatch} />}

        <Form
          action={`/venues/${get(venuePatch, 'id', '')}`}
          handleSuccess={this.handleSuccess}
          name="venue"
          patch={venuePatch}
          readOnly={isReadOnly}>
          <Field type="hidden" name="managingOffererId" />
          <div className="section">
            <h2 className="main-list-title">
              IDENTIFIANTS
              <span className="is-pulled-right is-size-7 has-text-grey">
                Les champs marqués d'un{' '}
                <span className="required-legend"> * </span> sont obligatoires
              </span>
            </h2>
            <div className="field-group">
              <Field label="SIRET" name="siret" type="siret" />
              <Field isExpanded label="Nom du lieu" name="name" required />
              <Field label="E-mail" name="bookingEmail" required type="email" />
            </div>
          </div>
          <div className="section">
            <h2 className="main-list-title">ADRESSE</h2>
            <div className="field-group">
              <Field
                isExpanded
                label="Numéro et voie"
                name="address"
                required
                type="geo"
                withMap
              />
              <Field
                autocomplete="postal-code"
                label="Code postal"
                name="postalCode"
                required
              />
              <Field
                autocomplete="address-level2"
                label="Ville"
                name="city"
                required
              />
              <Field label="Longitude" name="longitude" required />
              <Field label="Latitude" name="latitude" required />
            </div>
          </div>
          <hr />
          <div
            className="field is-grouped is-grouped-centered"
            style={{ justifyContent: 'space-between' }}>
            <div className="control">
              {isReadOnly ? (
                <NavLink
                  className="button is-secondary is-medium"
                  to={`/structures/${offererId}/lieux/${venueId}?modifie`}>
                  Modifier le lieu
                </NavLink>
              ) : (
                <CancelButton
                  className="button is-secondary is-medium"
                  to={
                    isNew
                      ? `/structures/${offererId}`
                      : `/structures/${offererId}/lieux/${venueId}`
                  }>
                  Annuler
                </CancelButton>
              )}
            </div>
            <div className="control">
              <div
                className="field is-grouped is-grouped-centered"
                style={{ justifyContent: 'space-between' }}>
                <div className="control">
                  {isReadOnly ? (
                    <NavLink
                      className="button is-primary is-medium"
                      to={`/structures/${offererId}`}>
                      Terminer
                    </NavLink>
                  ) : (
                    <SubmitButton className="button is-primary is-medium">
                      {isNew ? 'Créer' : 'Valider'}
                    </SubmitButton>
                  )}
                </div>
              </div>
            </div>
          </div>
        </Form>
      </Main>
    )
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  connect(
    (state, ownProps) => {
      const { offererId, venueId } = ownProps.match.params
      return {
        user: state.user,
        venuePatch: selectVenuePatchByVenueIdByOffererId(
          state,
          venueId,
          offererId
        ),
        offerer: offererSelector(state, offererId),
      }
    },
    {
      requestData,
      showNotification,
    }
  )
)(VenuePage)
