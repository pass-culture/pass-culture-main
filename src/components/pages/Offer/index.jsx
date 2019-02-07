import get from 'lodash.get'
import {
  CancelButton,
  closeModal,
  Field,
  Form,
  Icon,
  mergeErrors,
  mergeForm,
  pluralize,
  requestData,
  showModal,
  SubmitButton,
  withLogin,
} from 'pass-culture-shared'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import HeroSection from 'components/layout/HeroSection'
import Main from 'components/layout/Main'
import MediationsManager from './MediationsManager'
import EventOccurrencesAndStocksManager from './EventOccurrencesAndStocksManager'
import eventSelector from 'selectors/event'
import eventOccurrencesSelector from 'selectors/eventOccurrences'
import eventOrThingPatchSelector from 'selectors/eventOrThingPatch'
import offerSelector from 'selectors/offer'
import offererSelector from 'selectors/offerer'
import offerersSelector from 'selectors/offerers'
import providersSelector from 'selectors/providers'
import selectApiSearch from 'selectors/selectApiSearch'
import selectMusicSubOptionsByMusicType from 'selectors/selectMusicSubOptionsByMusicType'
import selectShowSubOptionsByShowType from 'selectors/selectShowSubOptionsByShowType'
import stocksSelector from 'selectors/stocks'
import thingSelector from 'selectors/thing'
import typesSelector from 'selectors/types'
import { typeSelector } from 'selectors/type'
import venueSelector from 'selectors/venue'
import venuesSelector from 'selectors/venues'
import { musicOptions, showOptions } from 'utils/edd'
import { offerNormalizer } from 'utils/normalizers'

const CONDITIONAL_FIELDS = {
  speaker: [
    'EventType.CONFERENCE_DEBAT_DEDICACE',
    'ThingType.PRATIQUE_ARTISTIQUE_ABO',
    'EventType.PRATIQUE_ARTISTIQUE',
  ],
  author: [
    'EventType.CINEMA',
    'EventType.MUSIQUE',
    'ThingType.MUSIQUE',
    'EventType.SPECTACLE_VIVANT',
    'ThingType.LIVRE_EDITION',
  ],
  visa: ['EventType.CINEMA'],
  isbn: ['ThingType.LIVRE_EDITION'],
  musicType: [
    'EventType.MUSIQUE',
    'ThingType.MUSIQUE',
    'ThingType.MUSIQUE_ABO',
  ],
  showType: ['EventType.SPECTACLE_VIVANT'],
  stageDirector: ['EventType.CINEMA', 'EventType.SPECTACLE_VIVANT'],
  performer: [
    'EventType.MUSIQUE',
    'ThingType.MUSIQUE',
    'EventType.SPECTACLE_VIVANT',
  ],
}

class OfferPage extends Component {
  constructor() {
    super()
    this.state = {
      isNew: false,
      isEventType: false,
      isOffererAndVenueSelectsReadOnly: true,
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
      selectedOfferType,
    } = nextProps
    const { eventId, thingId } = offer || {}

    const isEdit = search.indexOf('modifie') > -1
    const isNew = offerId === 'nouveau'
    const isEventType = get(selectedOfferType, 'type') === 'Event' || eventId
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
      history,
      dispatch,
      match: {
        params: { offerId },
      },
      offerers,
      venues,
      providers,
      search,
      types,
    } = this.props

    if (offerId !== 'nouveau') {
      dispatch(
        requestData('GET', `offers/${offerId}`, {
          key: 'offers',
          normalizer: offerNormalizer,
        })
      )
    } else if (search.venueId) {
      requestData('GET', `venues/${search.venueId}`, {
        normalizer: {
          managingOffererId: 'offerers',
        },
      })
    } else {
      let offerersPath = 'offerers'
      if (search.offererId) {
        offerersPath = `${offerersPath}/${search.offererId}`
      }

      dispatch(
        requestData('GET', offerersPath, {
          handleSuccess: (state, action) => {
            if (!get(state, 'data.venues.length')) {
              dispatch(
                showModal(
                  <div>
                    Vous devez avoir déjà enregistré un lieu dans une de vos
                    structures pour ajouter des offres
                  </div>,
                  {
                    onCloseClick: () => history.push('/structures'),
                  }
                )
              )
            }
          },
          handleFail,
          normalizer: { managedVenues: 'venues' },
        })
      )
    }

    if (offerers.length === 0 || venues.length === 0) {
      dispatch(
        requestData('GET', 'offerers', {
          normalizer: { managedVenues: 'venues' },
        })
      )
    }

    if (providers.length === 0) {
      dispatch(requestData('GET', 'providers'))
    }

    if (types.length === 0) {
      dispatch(requestData('GET', 'types'))
    }

    handleSuccess()
  }

  handleSuccess = (state, action) => {
    const { data, method } = action
    const { history, offer, venue } = this.props

    // PATCH
    if (method === 'PATCH') {
      history.push(`/offres/${offer.id}`)
      return
    }

    // POST
    if (method === 'POST') {
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

  handleOffererRedirect = () => {
    const { history, offer, search } = this.props
    const venueId = get(offer, 'venueId')
    if (venueId && !search.venueId) {
      history.push(`/offres/${offer.id}?lieu=${venueId}`)
      return
    }
  }

  handleShowManagerModal = () => {
    const {
      hasEventOrThing,
      dispatch,
      location: { search },
    } = this.props
    search.indexOf('gestion') > -1
      ? hasEventOrThing &&
        dispatch(
          showModal(<EventOccurrencesAndStocksManager />, {
            isUnclosable: true,
          })
        )
      : dispatch(closeModal())
  }

  setDefaultBookingEmailIfNew(prevProps) {
    if (!this.state.isNew) return
    const { dispatch, user, venue } = this.props
    if (!venue) return
    if (!prevProps || !prevProps.venue || venue.id !== prevProps.venue.id) {
      dispatch(
        mergeForm('offer', {
          bookingEmail: (venue && venue.bookingEmail) || user.email,
        })
      )
    }
  }

  componentDidMount() {
    this.handleOffererRedirect()
    this.handleShowManagerModal()
    this.setDefaultBookingEmailIfNew()
  }

  componentDidUpdate(prevProps) {
    const {
      dispatch,
      eventOccurrences,
      eventOrThingPatch,
      formOffererId,
      formVenueId,
      hasEventOrThing,
      location: { pathname, search },
      offer,
      offerer,
      offerTypeError,
      selectedOfferType,
      venue,
    } = this.props

    if (search.indexOf('gestion') > -1) {
      if (
        prevProps.offer !== offer ||
        prevProps.eventOccurrences !== eventOccurrences ||
        prevProps.location.pathname !== pathname ||
        prevProps.location.search !== search ||
        (hasEventOrThing && !prevProps.hasEventOrThing)
      ) {
        this.handleShowManagerModal()
      }
    }

    if (
      !formOffererId &&
      ((!offerer && prevProps.offerer) ||
        (!selectedOfferType && prevProps.selectedOfferType))
    ) {
      dispatch(
        mergeForm('offer', {
          offererId: null,
          venueId: null,
        })
      )
    }

    if (!formVenueId && (!venue && prevProps.venue)) {
      dispatch(
        mergeForm('offer', {
          venueId: null,
        })
      )
    }

    this.setDefaultBookingEmailIfNew(prevProps)

    if (
      get(eventOrThingPatch, 'type') &&
      !selectedOfferType &&
      !offerTypeError
    ) {
      dispatch(
        mergeErrors('offer', {
          type: [
            'Il y a eu un problème avec la création de cette offre: son type est incompatible avec le lieu enregistré.',
          ],
        })
      )
    }
  }

  hasConditionalField(fieldName) {
    if (!this.props.selectedOfferType) {
      return false
    }

    return (
      CONDITIONAL_FIELDS[fieldName].indexOf(
        this.props.selectedOfferType.value
      ) > -1
    )
  }

  render() {
    const {
      event,
      eventOccurrences,
      eventOrThingPatch,
      hasEventOrThing,
      location: { search },
      offer,
      offerer,
      offerers,
      stocks,
      thing,
      selectedOfferType,
      types,
      venue,
      venues,
      url,
      user,
      musicSubOptions,
      showSubOptions,
    } = this.props
    const { apiPath, isNew, isReadOnly, isEventType } = this.state
    const eventOrThingName = get(event, 'name') || get(thing, 'name')
    const offerId = get(offer, 'id')
    const offererId = get(offerer, 'id')
    const showAllForm = selectedOfferType || !isNew
    const venueId = get(venue, 'id')
    const isOfferActive = get(offer, 'isActive')
    const isOffererSelectReadOnly = typeof offererId !== 'undefined'
    const isVenueSelectReadOnly = typeof venueId !== 'undefined'
    const isVenueVirtual = get(venue, 'isVirtual')

    let title
    if (isNew) {
      title = 'Ajouter une offre'
      if (venueId) {
        if (isVenueVirtual) {
          title = title + ' en ligne'
        } else {
          title = title + ` pour ${get(venue, 'name')}`
        }
      } else if (offererId) {
        title = title + ` pour ${get(offerer, 'name')}`
      }
    } else {
      title = "Détails de l'offre"
    }

    return (
      <Main
        backTo={{ path: '/offres', label: 'Vos offres' }}
        name="offer"
        handleDataRequest={this.handleDataRequest}>
        <HeroSection
          subtitle={eventOrThingName && eventOrThingName.toUpperCase()}
          title={title}>
          <p className="subtitle">
            Renseignez les détails de cette offre, puis mettez-la en avant en
            ajoutant une ou plusieurs accroches.
          </p>

          <p className="subtitle">
            Attention : les offres payantes ne seront visibles auprès du public
            qu’à partir du début de l’expérimentation.
          </p>

          <Form
            action={apiPath}
            name="offer"
            handleSuccess={this.handleSuccess}
            patch={eventOrThingPatch}
            readOnly={isReadOnly}>
            <div className="field-group">
              <Field isExpanded label="Titre de l'offre" name="name" required />
              <Field
                label="Type"
                name="type"
                optionLabel="label"
                optionValue="value"
                options={types}
                placeholder={
                  get(eventOrThingPatch, 'type') && !selectedOfferType
                    ? get(eventOrThingPatch, 'offerTypeValue')
                    : "Sélectionnez un type d'offre"
                }
                readOnly={offerId && selectedOfferType}
                required
                sublabel="Le type d'offre ne peut pas être modifié une fois l'offre enregistrée."
                type="select"
              />
              {this.hasConditionalField('musicType') && (
                <Fragment>
                  <Field
                    label="Genre musical"
                    name="musicType"
                    options={musicOptions}
                    optionValue="code"
                    optionLabel="label"
                    setKey="extraData"
                    type="select"
                  />

                  {get(musicSubOptions, 'length') > 0 && (
                    <Field
                      label="Sous genre"
                      name="musicSubType"
                      options={musicSubOptions}
                      optionValue="code"
                      optionLabel="label"
                      setKey="extraData"
                      type="select"
                    />
                  )}
                </Fragment>
              )}

              {this.hasConditionalField('showType') && (
                <Fragment>
                  <Field
                    label="Type de spectacle"
                    name="showType"
                    options={showOptions}
                    optionValue="code"
                    optionLabel="label"
                    setKey="extraData"
                    type="select"
                  />

                  {get(showSubOptions, 'length') > 0 && (
                    <Field
                      type="select"
                      label="Sous type"
                      name="showSubType"
                      setKey="extraData"
                      options={showSubOptions}
                      optionValue="code"
                      optionLabel="label"
                    />
                  )}
                </Fragment>
              )}
              {!isNew && hasEventOrThing && (
                <div className="field is-horizontal field-text">
                  <div className="field-label">
                    <label className="label" htmlFor="input_offers_name">
                      <div className="subtitle">
                        {isEventType ? 'Dates :' : 'Stocks :'}
                      </div>
                    </label>
                  </div>
                  <div className="field-body">
                    <div className="control" style={{ paddingTop: '0.25rem' }}>
                      <span
                        className="nb-dates"
                        style={{ paddingTop: '0.25rem' }}>
                        {pluralize(
                          get(
                            isEventType ? eventOccurrences : stocks,
                            'length'
                          ),
                          isEventType ? 'date' : 'stock'
                        )}
                      </span>
                      <NavLink
                        className="button is-primary is-outlined is-small manage-stock"
                        to={`/offres/${offerId}?gestion`}>
                        <span className="icon">
                          <Icon svg="ico-calendar" />
                        </span>
                        <span>
                          {isEventType
                            ? 'Gérer les dates et les stocks'
                            : 'Gérer les stocks'}
                        </span>
                      </NavLink>
                    </div>
                  </div>
                </div>
              )}
            </div>
            {!isNew && <MediationsManager />}
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
                    readOnly={isOffererSelectReadOnly}
                    required
                    type="select"
                  />
                  {offerer && get(venues, 'length') === 0 && (
                    <div className="field is-horizontal">
                      <div className="field-label" />
                      <div className="field-body">
                        <p className="help is-danger">
                          {venue
                            ? "Erreur dans les données: Le lieu rattaché à cette offre n'est pas compatible avec le type de l'offre"
                            : 'Il faut obligatoirement une structure avec un lieu.'}
                          <Field type="hidden" name="__BLOCK_FORM__" required />
                        </p>
                      </div>
                    </div>
                  )}
                  <Field
                    label="Lieu"
                    name="venueId"
                    options={venues}
                    placeholder="Sélectionnez un lieu"
                    readOnly={isVenueSelectReadOnly}
                    required
                    type="select"
                  />
                  {(get(venue, 'isVirtual') || url) && (
                    <Field
                      isExpanded
                      label="URL"
                      name="url"
                      required
                      sublabel={
                        !isReadOnly &&
                        "Vous pouvez inclure {token} {email} et {offerId} dans l'URL, qui seront remplacés respectivement par le code de la contremarque, l'email de la personne ayant reservé et l'identifiant de l'offre"
                      }
                      type="text"
                    />
                  )}
                  {get(user, 'isAdmin') && (
                    <Field
                      label="Rayonnement national"
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
                  <Field
                    label="Email auquel envoyer les réservations"
                    name="bookingEmail"
                    type="email"
                    sublabel="Merci de laisser ce champ vide si vous ne souhaitez pas recevoir d'email lors des réservations"
                  />
                </div>
                <h2 className="main-list-title">Infos artistiques</h2>
                <div className="field-group">
                  <Field
                    displayMaxLength
                    isExpanded
                    label="Description"
                    maxLength={1000}
                    name="description"
                    rows={isReadOnly ? 1 : 5}
                    type="textarea"
                  />

                  {this.hasConditionalField('speaker') && (
                    <Field
                      type="text"
                      label="Intervenant"
                      name="speaker"
                      setKey="extraData"
                    />
                  )}

                  {this.hasConditionalField('author') && (
                    <Field
                      type="text"
                      label="Auteur"
                      name="author"
                      setKey="extraData"
                    />
                  )}

                  {this.hasConditionalField('visa') && (
                    <Field
                      isExpanded
                      label="Visa d'exploitation"
                      name="visa"
                      setKey="extraData"
                      sublabel="(obligatoire si applicable)"
                      type="text"
                    />
                  )}

                  {this.hasConditionalField('isbn') && (
                    <Field
                      isExpanded
                      label="ISBN"
                      name="isbn"
                      setKey="extraData"
                      sublabel="(obligatoire si applicable)"
                      type="text"
                    />
                  )}

                  {this.hasConditionalField('stageDirector') && (
                    <Field
                      isExpanded
                      label="Metteur en scène"
                      name="stageDirector"
                      setKey="extraData"
                    />
                  )}

                  {this.hasConditionalField('performer') && (
                    <Field
                      isExpanded
                      label="Interprète"
                      name="performer"
                      setKey="extraData"
                    />
                  )}
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
                    to={`/offres/${offerId}?modifie`}
                    className="button is-secondary is-medium">
                    Modifier l'offre
                  </NavLink>
                ) : (
                  <CancelButton
                    className="button is-secondary is-medium"
                    to={isNew ? '/offres' : `/offres/${offerId}`}>
                    Annuler
                  </CancelButton>
                )}
              </div>
              <div className="control">
                {isReadOnly ? (
                  <NavLink to="/offres" className="button is-primary is-medium">
                    Terminer {search.modifie && !isOfferActive && 'et activer'}
                  </NavLink>
                ) : (
                  showAllForm && (
                    <SubmitButton className="button is-primary is-medium">
                      Enregistrer{' '}
                      {isNew &&
                        'et passer ' +
                          (isEventType ? 'aux dates' : 'aux stocks')}
                    </SubmitButton>
                  )
                )}
              </div>
            </div>
          </Form>
        </HeroSection>
      </Main>
    )
  }
}

function mapStateToProps(state, ownProps) {
  const search = selectApiSearch(state, ownProps.location.search)

  const providers = providersSelector(state)

  const offerId = ownProps.match.params.offerId
  const offer = offerSelector(state, offerId)

  const eventId = get(offer, 'eventId')
  const event = eventSelector(state, eventId)

  const thingId = get(offer, 'thingId')
  const thing = thingSelector(state, thingId)

  const formVenueId = get(state, 'form.offer.venueId')
  const venueId = formVenueId || search.venueId

  const venue = venueSelector(state, venueId)

  const isVirtual = get(venue, 'isVirtual')
  const types = typesSelector(state, isVirtual)

  const offerTypeValue =
    get(state, 'form.offer.type') ||
    get(event, 'offerType.value') ||
    get(thing, 'offerType.value')

  const selectedOfferType = typeSelector(state, isVirtual, offerTypeValue)

  const formOffererId = get(state, 'form.offer.offererId')
  let offererId = formOffererId || search.offererId

  const venues = venuesSelector(state, offererId, selectedOfferType)

  offererId = offererId || get(venue, 'managingOffererId')

  const offerers = offerersSelector(state)
  const offerer = offererSelector(state, offererId)

  const eventOccurrences = eventOccurrencesSelector(state, offerId)

  const stocks = stocksSelector(state, offerId, event && eventOccurrences)

  const url =
    get(state, 'form.offer.url') || get(event, 'url') || get(thing, 'url')

  const user = state.user

  const hasEventOrThing = event || thing

  const eventOrThingPatch = eventOrThingPatchSelector(
    state,
    event,
    thing,
    offerer,
    venue
  )
  const extraData = get(state, 'form.offer.extraData') || {}

  const musicSubOptions =
    extraData.musicType && selectMusicSubOptionsByMusicType(extraData.musicType)
  const showSubOptions =
    extraData.showType && selectShowSubOptionsByShowType(extraData.showType)

  const offerTypeError = get(state, 'errors.offer.type')

  return {
    event,
    eventOccurrences,
    eventOrThingPatch,
    formOffererId,
    formVenueId,
    hasEventOrThing,
    musicSubOptions,
    offer,
    offerer,
    offerers,
    offerTypeError,
    providers,
    search,
    showSubOptions,
    stocks,
    thing,
    types,
    selectedOfferType,
    url,
    user,
    venue,
    venues,
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  connect(mapStateToProps)
)(OfferPage)
