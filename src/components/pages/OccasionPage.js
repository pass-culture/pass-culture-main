import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import MediationManager from '../MediationManager'
import OccasionForm from '../OccasionForm'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import Icon from '../layout/Icon'
import { resetForm } from '../../reducers/form'
import { showModal } from '../../reducers/modal'
import { showNotification } from '../../reducers/notification'
import eventSelector from '../../selectors/event'
import occurencesSelector from '../../selectors/occurences'
import offererSelector from '../../selectors/offerer'
import offerersSelector from '../../selectors/offerers'
import providersSelector from '../../selectors/providers'
import searchSelector from '../../selectors/search'
import thingSelector from '../../selectors/thing'
import typeSelector from '../../selectors/type'
import typesSelector from '../../selectors/types'
import venueSelector from '../../selectors/venue'
import venuesSelector from '../../selectors/venues'
import { NEW } from '../../utils/config'
import { getIsDisabled, optionify } from '../../utils/form'
import { eventNormalizer } from '../../utils/normalizers'
import { pluralize, updateQueryString } from '../../utils/string'

import Form from '../layout/Form'
import Field from '../layout/Field'
import Submit from '../layout/Submit'

const requiredEventAndThingFields = [
  'name',
  'type',
  'description'
]

const requiredEventFields = [
  'durationMinutes',
]

class OccasionPage extends Component {
  constructor () {
    super()
    this.state = {
      isReadOnly: true,
      hasNoVenue: false,
      isEventType: false,
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      match: { params: { feature } },
      isNew,
      occasion,
      type,
    } = nextProps
    const {
      eventId,
      thingId
    } = (occasion || {})
    const isEdit = feature === 'modifie'
    const isEventType = eventId || get(type, 'model') === 'EventType'
    const isReadOnly = !isNew && !isEdit

    const apiPath = isEventType
      ? `events${eventId ? `/${eventId}` : ''}`
      : `things${thingId ? `/${thingId}` : ''}`

    let requiredFields = requiredEventAndThingFields

    if (isEventType) {
      requiredFields = requiredFields.concat(requiredEventFields)
    }

    return {
      apiPath,
      isEventType,
      isReadOnly,
      requiredFields
    }
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      history,
      offerers,
      providers,
      requestData,
      showModal,
      typeOptions,
    } = this.props
    offerers.length === 0 && requestData(
      'GET',
      'offerers',
      {
        handleSuccess: (state, action) => {
          if (!get(state, 'data.venues.length')) {
            showModal(
              <div>
                Vous devez avoir déjà enregistré un lieu
                dans une de vos structures pour ajouter des offres
              </div>, {
                onCloseClick: () => history.push('/structures')
              })
          }
        },
        handleFail,
        normalizer: { managedVenues: 'venues' }
      }
    )
    providers.length === 0 && requestData('GET', 'providers')
    typeOptions.length === 0 && requestData('GET', 'types')

    handleSuccess()
  }

  handleFail = (state, action) => {
    this.props.showNotification({
      type: 'danger',
      text: 'Un problème est survenu lors de l\'enregistrement',
    })
  }

  handleSuccess = (state, action) => {
    const {
      data,
      method
    } = action
    const {
      occasion,
      history,
      showNotification,
      venue
    } = this.props
    const {
      isEventType
    } = this.state

    showNotification({
      text: 'Votre offre a bien été enregistrée',
      type: 'success'
    })

    // PATCH
    if (method === 'PATCH') {
      history.push(`/offres/${occasion.id}`)
      return
    }

    // POST
    if (isEventType && method === 'POST') {
      const { occasions } = (data || {})
      const occasion = occasions && occasions.find(o =>
        o.venueId === get(venue, 'id'))
      if (!occasion) {
        console.warn("Something wrong with returned data, we should retrieve the created occasion here")
        return
      }
      history.push(`/offres/${occasion.id}/dates?modifie`)
    }
  }

  componentDidUpdate () {
    const {
      history,
      offerer,
      search,
      venue
    } = this.props
    const { offererId, venueId } = this.props

    if (venue && venueId && venue.id !== venueId) {
      history.push({
        search: updateQueryString(search, { venueId })
      })
      return
    }
    if (offerer && offererId && offerer.id !== offererId) {
      history.push({
        search: updateQueryString(search, { offererId })
      })
    }
  }

  componentWillUnmount () {
    this.props.resetForm()
  }

  render () {
    const {
      event,
      isNew,
      location: { pathname, search },
      occasion,
      occurences,
      occasionIdOrNew,
      offerer,
      offerers,
      routePath,
      thing,
      type,
      typeOptions,
      venue,
      venues
    } = this.props
    const {
      extraData,
      name
    } = (event || thing || {})
    const {
      apiPath,
      isReadOnly,
      isEventType,
      requiredFields,
    } = this.state


    const showAllForm = type || !isNew

    const formData = Object.assign({}, event || thing, venue, occasion)

    return (
      <PageWrapper
        backTo={{path: `/offres${search}`, label: 'Vos offres'}}
        name='offer'
        handleDataRequest={this.handleDataRequest}
      >
        <div className='section'>
          <h1 className='pc-title'>
            {
              isNew
                ? "Ajouter une"
                : "Détails de l'"
            } offre
          </h1>
          <p className='subtitle'>
            Renseignez les détails de cette offre et mettez-la en avant en ajoutant une ou plusieurs accorches.
          </p>
          <Form name='occasion' handleSuccess={this.handleSuccess} handleFail={this.handleFail} action={apiPath} data={formData} readOnly={isReadOnly}>
            <div className='field-group'>
              <Field name='name' label="Titre de l'offre" required isExpanded/>
              <Field type='select' name='type' label='Type' required options={typeOptions} placeholder="Sélectionnez un type d'offre" optionLabel='label'/>
            </div>
            { !isNew && (
              <div className='field'>
                { event && (
                  <div className='field form-field is-horizontal'>
                    <div className='field-label'>
                      <label className="label" htmlFor="input_occasions_name">
                        <div className="subtitle">Dates :</div>
                      </label>
                    </div>
                    <div className='field-body'>
                      <div className='field'>
                        <div className='nb-dates'>
                          {pluralize(get(occurences, 'length'), 'date')}
                        </div>
                        <NavLink
                          className='button is-primary is-outlined is-small'
                          to={`${routePath}/dates`}
                        >
                          <span className='icon'><Icon svg='ico-calendar' /></span>
                          <span>Gérer les dates et les prix</span>
                        </NavLink>
                      </div>
                    </div>
                  </div>
                )}
                <MediationManager
                  occasion={occasion}
                  routePath={routePath}
                />
              </div>
            )}
            { showAllForm &&
              <div>
                <h2 className='pc-list-title'>
                  Infos pratiques
                </h2>
                <div className='field-group'>
                  <Field type='select' name='managingOffererId' label='Structure' required options={offerers} placeholder="Sélectionnez une structure" debug/>
                  { offerer && get(venues, 'length') === 0 ? (
                    <div className='field is-horizontal'>
                      <div className='field-label'></div>
                      <div className='field-body'>
                        <p className='help is-danger'>
                          Il faut obligatoirement une structure avec un lieu.
                        </p>
                      </div>
                    </div>
                    ) :
                    get(venues, 'length') > 0 && <Field type='select' name='venueId' label='Lieu' required options={venues} placeholder='Sélectionnez un lieu' /> }
                  { isEventType && (
                    <Field type='number' name='durationMinutes' label='Durée en minutes' required />
                  )}
                </div>
                <h2 className='pc-list-title'>Infos artistiques</h2>
                <div className='field-group'>
                  <Field type='textarea' name='description' label='Description' maxLength={750} required isExpanded />
                  <Field name='author' label='Auteur' isExpanded />
                  {
                    isEventType && [
                      <Field key={0} name='stageDirector' label='Metteur en scène' isExpanded />,
                      <Field key={1} name='performer' label='Interprète' isExpanded />
                    ]
                  }
                </div>
              </div>
            }

            <hr />
            <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
              <div className="control">
                { isReadOnly ? (
                  <NavLink to={`${pathname}/modifie${search}`}
                    className='button is-secondary is-medium'>
                    Modifier l'offre
                  </NavLink>
                ) : (
                  <NavLink
                    className="button is-secondary is-medium"
                    to={`/offres${search}`}>
                    Annuler
                  </NavLink>
                )}
              </div>
              <div className="control">
                { isReadOnly ? (
                  <NavLink to={`/offres${search}`} className='button is-primary is-medium'>
                    Terminer
                  </NavLink>
                ) : (
                  <Submit className="button is-primary is-medium">Enregistrer</Submit>
                )}
              </div>
            </div>
          </Form>
        </div>
      </PageWrapper>
    )
  }
}

export default compose(
  withCurrentOccasion,
  connect(
    (state, ownProps) => {
      const search = searchSelector(state, ownProps.location.search)
      const occasionId = get(ownProps, 'occasion.id') || NEW

      const providers = providersSelector(state)

      const eventId = get(ownProps, 'occasion.eventId')
      const event = eventSelector(state, eventId)

      const thingId = get(ownProps, 'occasion.thingId')
      const thing = thingSelector(state, thingId)

      const typeOptions = typesSelector(state)
      const typeName = get(state, 'form.occasion.data.type') || get(event, 'type') || get(thing, 'type')
      const type = typeSelector(state, eventId, thingId, typeName)

      const occurences = occurencesSelector(state, venueId, eventId)

      let offererId = get(state, 'form.occasion.data.managingOffererId') || search.offererId

      const venues = venuesSelector(state, offererId)
      const venueId = get(state, 'form.occasion.data.venueId') || search.venueId || get(event, 'venueId') || get(thing, 'venueId')
      const venue = venueSelector(state, venueId)

      offererId = offererId || get(venue, 'managingOffererId')

      const offerers = offerersSelector(state)
      const offerer = offererSelector(state, offererId)

      return {
        search,
        providers,
        event,
        thing,
        occurences,
        venues,
        venue,
        offerers,
        offerer,
        typeOptions,
        type,
      }
    },
    {
      resetForm,
      showModal,
      showNotification
    }
  )
)(OccasionPage)
