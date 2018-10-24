import classnames from 'classnames'
import get from 'lodash.get'
import {
  CancelButton,
  closeNotification,
  Icon,
  Field,
  Form,
  requestData,
  showNotification,
  SubmitButton,
  withLogin,
} from 'pass-culture-shared'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import HeroSection from '../layout/HeroSection'
import Main from '../layout/Main'
import VenueProvidersManager from '../managers/VenueProvidersManager'
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
      isEdit,
      isNew,
      isReadOnly,
    }
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      dispatch,
      match: {
        params: { offererId, venueId },
      },
    } = this.props
    if (venueId !== 'nouveau') {
      dispatch(
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
      )
    } else {
      return handleSuccess()
    }
  }

  handleSuccess = (state, action) => {
    const { dispatch, history, offerer } = this.props
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

    const createOfferPathname = `/offres/nouveau?lieu=${venueId}`

    const text =
      get(action, 'method') === 'POST' ? (
        <p>
          Lieu créé. Vous pouvez maintenant y{' '}
          <NavLink
            to={createOfferPathname}
            onClick={() => dispatch(closeNotification())}>
            créer une offre
          </NavLink>
          , ou en importer automatiquement.
        </p>
      ) : (
        'Lieu modifié avec succès !'
      )

    dispatch(
      showNotification({
        text,
        type: 'success',
      })
    )
    // TODO: do it in the way that the notification
    // is displayed in the next page an disapeear when
    // the user is after changing to another page
  }

  render() {
    const {
      formGeo,
      formLatitude,
      formLongitude,
      formSire,
      match: {
        params: { offererId, venueId },
      },
      name,
      offerer,
      venuePatch,
    } = this.props
    const { isEdit, isNew, isReadOnly } = this.state

    const savedVenueId = get(venuePatch, 'id')
    // TODO: offerer should provide a offerer.userRight
    // to determine if it can edit iban stuff
    // let s make false for now
    const hasAlreadyRibUploaded =
      get(venuePatch, 'iban') && get(venuePatch, 'thumbCount')
    const isRibEditable = !isReadOnly && false
    const isSiretReadOnly = get(venuePatch, 'siret')
    const isSiretSkipping = !venueId && name && !formSire
    const isFieldReadOnlyBecauseFrozenFromSiret =
      isReadOnly || formSire || (isEdit && get(venuePatch, 'siret'))
    const isReadOnlyFromGeoOrSiren =
      formGeo || isFieldReadOnlyBecauseFrozenFromSiret
    const isLatitudeReadOnlyFromGeoOrSiren =
      formGeo || (isFieldReadOnlyBecauseFrozenFromSiret && formLatitude)
    const isLongitudeReadOnlyFromGeoOrSiren =
      formGeo || (isFieldReadOnlyBecauseFrozenFromSiret && formLongitude)

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
        <HeroSection subtitle={get(venuePatch, 'name')} title="Lieu">
          {isNew && (
            <p className="subtitle">Ajoutez un lieu où accéder à vos offres.</p>
          )}

          {get(offerer, 'id') &&
            savedVenueId && (
              <NavLink
                to={`/offres/nouveau?lieu=${venuePatch.id}`}
                className="cta button is-primary">
                <span className="icon">
                  <Icon svg="ico-offres-w" />
                </span>
                <span>Créer une offre</span>
              </NavLink>
            )}
        </HeroSection>

        {!isNew && <VenueProvidersManager venue={venuePatch} />}

        {!get(venuePatch, 'isVirtual') && (
          <Form
            action={`/venues/${savedVenueId || ''}`}
            handleSuccess={this.handleSuccess}
            name="venue"
            normalizer={venueNormalizer}
            patch={venuePatch}
            readOnly={isReadOnly}>
            {isNew && <Field type="hidden" name="managingOffererId" />}
            <div className="section">
              <h2 className="main-list-title is-relative">
                IDENTIFIANTS
                <span className="is-pulled-right is-size-7 has-text-grey">
                  Les champs marqués d'un{' '}
                  <span className="required-legend"> * </span> sont obligatoires
                </span>
              </h2>
              <div className="field-group">
                <Field
                  className={classnames({ 'is-invisible': isSiretSkipping })}
                  label="SIRET (si applicable)"
                  name="siret"
                  readOnly={isSiretReadOnly}
                  required={!this.props.formComment}
                  renderInfo={() => {
                    if (isReadOnly) {
                      return
                    }
                    if (isFieldReadOnlyBecauseFrozenFromSiret) {
                      return (
                        <span
                          className="button"
                          data-place="bottom"
                          data-tip="<p>Il n'est pas possible de modifier le nom, l'addresse et la géolocalisation du lieu quand un siret est rentré.</p>"
                          data-type="info">
                          <Icon svg="picto-info" />
                        </span>
                      )
                    }
                    return (
                      !isSiretReadOnly && (
                        <span
                          className="button"
                          data-place="bottom"
                          data-tip="<div><p>Saisissez ici le SIRET du lieu lié à votre structure pour retrouver ses informations automatiquement.</p>
<p>Si les informations ne correspondent pas au SIRET saisi, <a href='mailto:pass@culture.gouv.fr?subject=Question%20SIRET'> contactez notre équipe</a>.</p></div>"
                          data-type="info">
                          <Icon svg="picto-info" />
                        </span>
                      )
                    )
                  }}
                  type="siret"
                />
                <Field
                  isExpanded
                  label="Nom"
                  name="name"
                  readOnly={isFieldReadOnlyBecauseFrozenFromSiret}
                  required
                />
                <Field
                  label="E-mail"
                  name="bookingEmail"
                  required
                  renderInfo={() => {
                    if (isReadOnly) {
                      return
                    }
                    return (
                      !isSiretReadOnly && (
                        <span
                          className="button"
                          data-tip="<p>Cette adresse recevra les e-mails de notification de réservation (sauf si une autre adresse différente est saisie lors de la création d'une offre)</p>"
                          data-place="bottom"
                          data-type="info">
                          <Icon svg="picto-info" />
                        </span>
                      )
                    )
                  }}
                  type="email"
                />
                <Field
                  label="Commentaire (si pas de SIRET)"
                  name="comment"
                  readOnly={formSire}
                  type="textarea"
                  required={!this.props.formSiret}
                />
              </div>
            </div>

            <div className="section">
              <h2 className="main-list-title">
                INFORMATIONS BANCAIRES
                <span className="is-pulled-right is-size-7 has-text-grey">
                  {isRibEditable ? (
                    <Fragment>
                      Les champs marqués d'un{' '}
                      <span className="required-legend"> * </span> sont
                      obligatoires
                    </Fragment>
                  ) : (
                    "Vous avez besoin d'être administrateur de la structure pour editer le rib et l'iban."
                  )}
                </span>
              </h2>
              <div className="field-group">
                <Field
                  label="BIC"
                  name="bic"
                  readOnly={!isRibEditable}
                  type="bic"
                />
                <Field
                  isExpanded
                  label="IBAN"
                  name="iban"
                  readOnly={!isRibEditable}
                  type="iban"
                />
                {false && (
                  <Field
                    isExpanded
                    label="Justificatif"
                    name="rib"
                    readOnly={isReadOnly || !isRibEditable}
                    uploaded={hasAlreadyRibUploaded}
                    type="file"
                  />
                )}
              </div>
            </div>

            <div className="section">
              <h2 className="main-list-title">ADRESSE</h2>
              <div className="field-group">
                <Field
                  isExpanded
                  label="Numéro et voie"
                  latitude={formLatitude}
                  longitude={formLongitude}
                  name="address"
                  readOnly={isFieldReadOnlyBecauseFrozenFromSiret}
                  required
                  type="geo"
                  withMap
                />
                <Field
                  autocomplete="postal-code"
                  label="Code postal"
                  name="postalCode"
                  readOnly={isReadOnlyFromGeoOrSiren}
                  required
                />
                <Field
                  autocomplete="address-level2"
                  label="Ville"
                  name="city"
                  readOnly={isReadOnlyFromGeoOrSiren}
                  required
                />
                <Field
                  label="Latitude"
                  name="latitude"
                  readOnly={isLatitudeReadOnlyFromGeoOrSiren}
                  required
                />
                <Field
                  label="Longitude"
                  name="longitude"
                  readOnly={isLongitudeReadOnlyFromGeoOrSiren}
                  required
                />
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
              {savedVenueId && (
                <div className="control">
                  <div
                    className="field is-grouped is-grouped-centered"
                    style={{ justifyContent: 'space-between' }}>
                    <div className="control">
                      <NavLink
                        className="button is-secondary is-medium"
                        to={`/offres/nouveau?lieu=${venueId}`}>
                        Créer une offre dans ce lieu
                      </NavLink>
                    </div>
                  </div>
                </div>
              )}
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
        )}
      </Main>
    )
  }
}

function mapStateToProps(state, ownProps) {
  const { offererId, venueId } = ownProps.match.params
  return {
    formGeo: get(state, 'form.venue.geo'),
    formLatitude: get(state, 'form.venue.latitude'),
    formLongitude: get(state, 'form.venue.longitude'),
    formSire: get(state, `form.venue.sire`),
    formSiret: get(state, 'form.venue.siret'),
    formComment: get(state, 'form.venue.comment'),
    name: get(state, `form.venue.name`),
    offerer: offererSelector(state, offererId),
    user: state.user,
    venuePatch: selectVenuePatchByVenueIdByOffererId(state, venueId, offererId),
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  connect(mapStateToProps)
)(VenuePage)
