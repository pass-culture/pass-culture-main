import classnames from 'classnames'
import get from 'lodash.get'
import {
  CancelButton,
  closeNotification,
  Field,
  Form,
  Icon,
  showNotification,
  SubmitButton,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import VenueProvidersManager from './VenueProvidersManager'
import HeroSection from 'components/layout/HeroSection'
import Main from 'components/layout/Main'
import { offererNormalizer, venueNormalizer } from 'utils/normalizers'
import {
  formatPatch,
  VENUE_EDIT_PATCH_KEYS,
  VENUE_NEW_PATCH_KEYS,
} from 'utils/formatPatch'

class Venue extends Component {
  constructor() {
    super()
    this.state = {
      isLoading: false,
      isNew: false,
      isRead: true,
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
    const isRead = !isNew && !isEdit

    return {
      isEdit,
      isNew,
      isRead,
    }
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      dispatch,
      match: {
        params: { offererId, venueId },
      },
    } = this.props

    if (!this.state.isNew) {
      dispatch(
        requestData({
          apiPath: `/offerers/${offererId}`,
          handleFail,
          handleSuccess: () => {
            dispatch(
              requestData({
                apiPath: `/venues/${venueId}`,
                handleSuccess,
                handleFail,
                normalizer: venueNormalizer,
              })
            )
          },
          normalizer: offererNormalizer,
        })
      )
      dispatch(requestData({ apiPath: `/userOfferers/${offererId}` }))
    } else {
      return handleSuccess()
    }
  }

  handleSuccess = (state, action) => {
    const { dispatch, history, offerer } = this.props
    const {
      config: { method },
      payload: { datum },
    } = action
    const offererId = get(offerer, 'id')
    const venueId = get(datum, 'id')

    const redirectUrl = this.buildRedirectUrl(offererId, venueId, method)
    history.push(redirectUrl)

    const notificationMessage = this.buildNotificationMessage(venueId, method)

    dispatch(
      showNotification({
        text: notificationMessage,
        type: 'success',
      })
    )
  }

  buildNotificationMessage = (venueId, method) => {
    const { dispatch } = this.props
    const isVenueCreated = method === 'POST'

    const venueCreatedMessage = (
      <p>
        Lieu créé. Vous pouvez maintenant y{' '}
        <NavLink
          to={`/offres/creation?lieu=${venueId}`}
          onClick={() => dispatch(closeNotification())}>
          créer une offre
        </NavLink>
        , ou en importer automatiquement.
      </p>
    )
    const venueModifiedMessage = 'Lieu modifié avec succès !'

    return isVenueCreated ? venueCreatedMessage : venueModifiedMessage
  }

  buildRedirectUrl = (offererId, venueId, method) => {
    const offererPath = `/structures/${offererId}`

    if (method === 'POST' || method === 'PATCH') {
      return `${offererPath}/lieux/${venueId}`
    }

    return offererPath
  }

  buildBackToInfos = (offerer, offererId) => {
    const offererName = get(offerer, 'name')

    return {
      label: offererName,
      path: `/structures/${offererId}`,
    }
  }

  checkIfVenueExists = venueId => {
    return !!venueId
  }

  render() {
    const {
      adminUserOfferer,
      formGeo,
      formLatitude,
      formLongitude,
      formSiret,
      match: {
        params: { offererId, venueId },
      },
      name,
      offerer,
      venuePatch,
    } = this.props

    const { isEdit, isNew, isRead } = this.state
    const patchConfig = { isNew, isEdit }

    const venuePatchId = get(venuePatch, 'id')
    const venuePatchSiret = get(venuePatch, 'siret')
    const venuePatchName = get(venuePatch, 'name')
    const venuePatchIsVirtual = get(venuePatch, 'isVirtual')

    const areBankInfosReadOnly = isRead || !adminUserOfferer
    const isCommentRequired = !venueId && name && !formSiret

    const isFieldReadOnlyBecauseFrozenFormSiret =
      isRead || formSiret || (isEdit && venuePatchSiret)
    const isReadFromGeoOrSiren =
      formGeo || isFieldReadOnlyBecauseFrozenFormSiret
    const isLatitudeReadOnlyFromGeoOrSiren =
      formGeo || (isFieldReadOnlyBecauseFrozenFormSiret && formLatitude)
    const isLongitudeReadOnlyFromGeoOrSiren =
      formGeo || (isFieldReadOnlyBecauseFrozenFormSiret && formLongitude)

    return (
      <Main
        backTo={this.buildBackToInfos(offerer, offererId)}
        name="venue"
        handleDataRequest={this.handleDataRequest}>
        <HeroSection subtitle={venuePatchName} title="Lieu">
          {isNew && (
            <p className="subtitle">Ajoutez un lieu où accéder à vos offres.</p>
          )}

          {this.checkIfVenueExists(venuePatchId) && (
            <NavLink
              to={`/offres/creation?lieu=${venuePatchId}`}
              className="cta button is-primary">
              <span className="icon">
                <Icon svg="ico-offres-w" />
              </span>
              <span>Créer une offre</span>
            </NavLink>
          )}
        </HeroSection>

        {!isNew && <VenueProvidersManager venue={venuePatch} />}

        {!venuePatchIsVirtual && (
          <Form
            action={`/venues/${venuePatchId || ''}`}
            formatPatch={patch =>
              formatPatch(
                patch,
                patchConfig,
                VENUE_NEW_PATCH_KEYS,
                VENUE_EDIT_PATCH_KEYS
              )
            }
            handleSuccess={this.handleSuccess}
            name="venue"
            normalizer={venueNormalizer}
            patch={venuePatch}
            readOnly={isRead}>
            {isNew && <Field type="hidden" name="managingOffererId" />}
            <div className="section">
              <h2 className="main-list-title is-relative">
                IDENTIFIANTS
                {!isRead && (
                  <span className="is-pulled-right is-size-7 has-text-grey">
                    Les champs marqués d'un{' '}
                    <span className="required-legend"> * </span> sont
                    obligatoires
                  </span>
                )}
              </h2>

              <div className="field-group">
                <Field
                  className={classnames({ 'is-invisible': isCommentRequired })}
                  label="SIRET (si applicable)"
                  name="siret"
                  readOnly={venuePatchSiret}
                  renderInfo={() => {
                    if (isFieldReadOnlyBecauseFrozenFormSiret) {
                      return (
                        <span
                          className="button"
                          data-place="bottom"
                          data-tip="<p>Il n'est pas possible de modifier le nom, l'addresse et la géolocalisation du lieu quand un siret est renseigné.</p>"
                          data-type="info">
                          <Icon svg="picto-info" />
                        </span>
                      )
                    }

                    return (
                      !venuePatchSiret && (
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
                  readOnly={isFieldReadOnlyBecauseFrozenFormSiret}
                  required
                />
                <Field label="Nom d'usage" name="publicName" type="textarea" />
                <Field
                  label="E-mail"
                  name="bookingEmail"
                  renderInfo={() => {
                    return (
                      !venuePatchSiret && (
                        <span
                          className="button"
                          data-tip="<p>Cette adresse recevra les e-mails de notification de réservation (sauf si une adresse différente est saisie lors de la création d'une offre)</p>"
                          data-place="bottom"
                          data-type="info">
                          <Icon svg="picto-info" />
                        </span>
                      )
                    )
                  }}
                  type="email"
                  required
                />
                {(isNew || (isEdit && !venuePatchSiret)) && (
                  <Field
                    label="Commentaire (si pas de SIRET)"
                    name="comment"
                    readOnly={formSiret}
                    type="textarea"
                    required={!formSiret}
                  />
                )}
              </div>
            </div>

            <div className="section">
              <h2 className="main-list-title">
                INFORMATIONS BANCAIRES
                <span className="is-pulled-right is-size-7 has-text-grey">
                  {!adminUserOfferer &&
                    "Vous avez besoin d'être administrateur de la structure pour éditer ces informations."}
                </span>
              </h2>

              <div className="field-group">
                <Field
                  label="BIC"
                  name="bic"
                  readOnly={areBankInfosReadOnly}
                  type="bic"
                />
                <Field
                  isExpanded
                  label="IBAN"
                  name="iban"
                  readOnly={areBankInfosReadOnly}
                  type="iban"
                />
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
                  readOnly={isFieldReadOnlyBecauseFrozenFormSiret}
                  required
                  type="geo"
                  withMap
                />
                <Field
                  autocomplete="postal-code"
                  label="Code postal"
                  name="postalCode"
                  readOnly={isReadFromGeoOrSiren}
                  required
                />
                <Field
                  autocomplete="address-level2"
                  label="Ville"
                  name="city"
                  readOnly={isReadFromGeoOrSiren}
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

            <div
              className="field is-grouped is-grouped-centered"
              style={{ justifyContent: 'space-between' }}>
              <div className="control">
                {isRead ? (
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
              {venuePatchId && (
                <div className="control">
                  <div
                    className="field is-grouped is-grouped-centered"
                    style={{ justifyContent: 'space-between' }}>
                    <div className="control">
                      <NavLink
                        className="button is-secondary is-medium"
                        to={`/offres/creation?lieu=${venueId}`}>
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
                    {isRead ? (
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

export default Venue
