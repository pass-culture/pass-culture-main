import get from 'lodash.get'
import {
  CancelButton,
  closeModal,
  Field,
  Form,
  Icon,
  requestData,
  showModal,
  showNotification,
  SubmitButton,
  withLogin,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Main from '../layout/Main'
import MediationManager from '../managers/MediationManager'
import OccurrenceManager from '../managers/OccurrenceManager'
import eventSelector from '../../selectors/event'
import occurrencesSelector from '../../selectors/occurrences'
import offerSelector from '../../selectors/offer'
import offererSelector from '../../selectors/offerer'
import offerersSelector from '../../selectors/offerers'
import providersSelector from '../../selectors/providers'
import searchSelector from '../../selectors/search'
import thingSelector from '../../selectors/thing'
import typesSelector from '../../selectors/types'
import typeSelector from '../../selectors/type'
import venueSelector from '../../selectors/venue'
import venuesSelector from '../../selectors/venues'
import { offerNormalizer } from '../../utils/normalizers'
import { pluralize } from '../../utils/string'

class OfferPage extends Component {
  constructor() {
    super()
    this.state = {
      isNew: false,
      isEventType: false,
      isReadOnly: true,
    }
  }

  static getDerivedStateFromProps(nextProps) {
    const {
      location: { search },
      match: {
        params: { offerId },
      },
      offer,
      type,
    } = nextProps
    const { eventId, thingId } = offer || {}

    const isEdit = search.indexOf('modifie') > -1
    const isNew = offerId === 'nouveau'
    const isEventType = get(type, 'type') === 'Event' || eventId
    const isReadOnly = !isNew && !isEdit

    const apiPath = isEventType
      ? `events/${eventId || ''}`
      : `things/${thingId || ''}`

    return {
      apiPath,
      isEventType,
      isNew,
      isReadOnly,
    }
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      match: {
        params: { offerId },
      },
      history,
      offer,
      offerers,
      providers,
      requestData,
      showModal,
      types,
    } = this.props
    !offer &&
      offerId !== 'nouveau' &&
      requestData('GET', `offers/${offerId}`, {
        key: 'offers',
        normalizer: offerNormalizer,
      })
    offerers.length === 0 &&
      requestData('GET', 'offerers', {
        handleSuccess: (state, action) => {
          if (!get(state, 'data.venues.length')) {
            showModal(
              <div>
                Vous devez avoir déjà enregistré un lieu dans une de vos
                structures pour ajouter des offres
              </div>,
              {
                onCloseClick: () => history.push('/structures'),
              }
            )
          }
        },
        handleFail,
        normalizer: { managedVenues: 'venues' },
      })
    providers.length === 0 && requestData('GET', 'providers')
    types.length === 0 && requestData('GET', 'types')

    handleSuccess()
  }

  handleFail = (state, action) => {
    this.props.showNotification({
      type: 'danger',
      text: "Un problème est survenu lors de l'enregistrement",
    })
  }

  handleSuccess = (state, action) => {
    const { data, method } = action
    const { history, offer, showNotification, venue } = this.props
    const { isEventType } = this.state

    showNotification({
      text: 'Votre offre a bien été enregistrée',
      type: 'success',
    })

    // PATCH
    if (method === 'PATCH') {
      history.push(`/offres/${offer.id}`)
      return
    }

    // POST
    if (isEventType && method === 'POST') {
      const { offers } = data || {}
      const offer = offers && offers.find(o => o.venueId === get(venue, 'id'))
      if (!offer) {
        console.warn(
          'Something wrong with returned data, we should retrieve the created offer here'
        )
        return
      }
      history.push(`/offres/${offer.id}?gestion`)
    }
  }

  handleShowOccurrencesModal = () => {
    const {
      location: { search },
      showModal,
    } = this.props
    search.indexOf('gestion') > -1
      ? showModal(<OccurrenceManager />, {
          isUnclosable: true,
        })
      : closeModal()
  }

  componentDidMount() {
    this.handleShowOccurrencesModal()
  }

  componentDidUpdate(prevProps) {
    const {
      location: { pathname, search },
      offer,
      occurrences,
    } = this.props

    if (search.indexOf('gestion') > -1) {
      if (
        prevProps.offer !== offer ||
        prevProps.occurrences !== occurrences ||
        prevProps.location.pathname !== pathname ||
        prevProps.location.search !== search
      ) {
        this.handleShowOccurrencesModal()
      }
    }
  }

  render() {
    const {
      event,
      location: { search },
      occurrences,
      offer,
      offerer,
      offerers,
      thing,
      type,
      types,
      venues,
      user,
    } = this.props
    const { apiPath, isNew, isReadOnly, isEventType } = this.state

    const showAllForm = type || !isNew

    return (
      <Main
        backTo={{ path: `/offres${search}`, label: 'Vos offres' }}
        name="offer"
        handleDataRequest={this.handleDataRequest}>
        <div className="section">
          <h1 className="main-title">
            {isNew ? 'Ajouter une offre' : "Détails de l'offre"}
          </h1>
          <p className="subtitle">
            Renseignez les détails de cette offre et mettez-la en avant en
            ajoutant une ou plusieurs accorches.
          </p>
          <Form
            action={apiPath}
            name="offer"
            handleSuccess={this.handleSuccess}
            handleFail={this.handleFail}
            patch={event || thing}
            readOnly={isReadOnly}>
            <div className="field-group">
              <Field name="name" label="Titre de l'offre" required isExpanded />
              <Field
                label="Type"
                name="type"
                optionLabel="label"
                optionValue="value"
                options={types}
                placeholder="Sélectionnez un type d'offre"
                required
                type="select"
              />
            </div>
            {!isNew && (
              <div className="field">
                {event && (
                  <div className="field form-field is-horizontal">
                    <div className="field-label">
                      <label className="label" htmlFor="input_offers_name">
                        <div className="subtitle">Dates :</div>
                      </label>
                    </div>
                    <div className="field-body">
                      <div className="field">
                        <div className="nb-dates">
                          {pluralize(get(occurrences, 'length'), 'date')}
                        </div>
                        <NavLink
                          className="button is-primary is-outlined is-small"
                          to={`/offres/${get(offer, 'id')}?gestion`}>
                          <span className="icon">
                            <Icon svg="ico-calendar" />
                          </span>
                          <span>Gérer les dates et les prix</span>
                        </NavLink>
                      </div>
                    </div>
                  </div>
                )}
                <MediationManager />
              </div>
            )}
            {showAllForm && (
              <div>
                <h2 className="main-list-title">Infos pratiques</h2>
                <div className="field-group">
                  <Field
                    debug
                    label="Structure"
                    name="offererId"
                    options={offerers}
                    placeholder="Sélectionnez une structure"
                    required
                    type="select"
                  />
                  {offerer && get(venues, 'length') === 0 ? (
                    <div className="field is-horizontal">
                      <div className="field-label" />
                      <div className="field-body">
                        <p className="help is-danger">
                          Il faut obligatoirement une structure avec un lieu.
                        </p>
                      </div>
                    </div>
                  ) : (
                    get(venues, 'length') > 0 && (
                      <Field
                        label="Lieu"
                        name="venueId"
                        options={venues}
                        placeholder="Sélectionnez un lieu"
                        required
                        type="select"
                      />
                    )
                  )}
                  {get(user, 'isAdmin') && (
                    <Field
                      label="Offre à rayonnement national"
                      name="isNational"
                      type="checkbox"
                    />
                  )}
                  {isEventType && (
                    <Field
                      label="Durée en minutes"
                      name="durationMinutes"
                      required
                      type="number"
                    />
                  )}
                </div>
                <h2 className="main-list-title">Infos artistiques</h2>
                <div className="field-group">
                  <Field
                    isExpanded
                    label="Description"
                    maxLength={750}
                    name="description"
                    required
                    type="textarea"
                  />
                  <Field name="author" label="Auteur" isExpanded />
                  {isEventType && [
                    <Field
                      isExpanded
                      key={0}
                      label="Metteur en scène"
                      name="stageDirector"
                    />,
                    <Field
                      isExpanded
                      key={1}
                      label="Interprète"
                      name="performer"
                    />,
                  ]}
                </div>
              </div>
            )}

            <hr />
            <div
              className="field is-grouped is-grouped-centered"
              style={{ justifyContent: 'space-between' }}>
              <div className="control">
                {isReadOnly ? (
                  <NavLink
                    to={`/offres/${get(offer, 'id')}?modifie`}
                    className="button is-secondary is-medium">
                    Modifier l'offre
                  </NavLink>
                ) : (
                  <CancelButton
                    className="button is-secondary is-medium"
                    to={isNew ? '/offres' : `/offres/${get(offer, 'id')}`}>
                    Annuler
                  </CancelButton>
                )}
              </div>
              <div className="control">
                {isReadOnly ? (
                  <NavLink to="/offres" className="button is-primary is-medium">
                    Terminer
                  </NavLink>
                ) : (
                  <SubmitButton className="button is-primary is-medium">
                    Enregistrer
                  </SubmitButton>
                )}
              </div>
            </div>
          </Form>
        </div>
      </Main>
    )
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  connect(
    (state, ownProps) => {
      const search = searchSelector(state, ownProps.location.search)

      const providers = providersSelector(state)

      const offer = offerSelector(state, ownProps.match.params.offerId)

      const eventId = get(offer, 'eventId')
      const event = eventSelector(state, eventId)

      const thingId = get(offer, 'thingId')
      const thing = thingSelector(state, thingId)

      const types = typesSelector(state)

      const typeValue =
        get(state, 'form.offer.type') ||
        get(event, 'type') ||
        get(thing, 'type')

      const type = typeSelector(state, typeValue)

      let offererId = get(state, 'form.offer.offererId') || search.offererId

      const venues = venuesSelector(state, offererId)
      const venueId =
        get(state, 'form.offer.venueId') ||
        search.venueId ||
        get(event, 'venueId') ||
        get(thing, 'venueId')
      const venue = venueSelector(state, venueId)

      offererId = offererId || get(venue, 'managingOffererId')

      const offerers = offerersSelector(state)
      const offerer = offererSelector(state, offererId)

      const occurrences = occurrencesSelector(
        state,
        ownProps.match.params.offerId
      )

      const user = state.user

      return {
        search,
        providers,
        event,
        thing,
        occurrences,
        offer,
        venues,
        venue,
        offerers,
        offerer,
        types,
        type,
        user,
      }
    },
    {
      showModal,
      closeModal,
      requestData,
      showNotification,
    }
  )
)(OfferPage)
