import get from 'lodash.get'
import React, { Component } from 'react'
import ReactMarkdown from 'react-markdown'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'


import OccurenceManager from '../OccurenceManager'
import withLogin from '../hocs/withLogin'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import Icon from '../layout/Icon'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { mergeForm, resetForm } from '../../reducers/form'
import { showModal } from '../../reducers/modal'
import { showNotification } from '../../reducers/notification'
import { SUCCESS } from '../../reducers/queries'
import selectEventOccurences from '../../selectors/eventOccurences'
import selectOffererOptions from '../../selectors/offererOptions'
import selectSelectedOffererId from '../../selectors/selectedOffererId'
import selectSelectedVenueId from '../../selectors/selectedVenueId'
import selectSelectedVenues from '../../selectors/selectedVenues'
import selectVenueOptions from '../../selectors/venueOptions'
import { API_URL } from '../../utils/config'

const mediationExplanation = `
  **L'accroche permet d'afficher votre offre "à la une" de l'app**, et la rend visuellement plus attrayante. C'est une image, une citation, ou une vidéo, intrigante, percutante, séduisante... en un mot : accrocheuse.

  Les accroches font la **spécificité du Pass Culture**. Prenz le temps de les choisir avec soin !
`

const requiredFields = [
  'name',
  'type',
  'durationMinutes',
  'description',
  'contactName',
  'contactEmail',
]

class OfferPage extends Component {
  constructor () {
    super()
    this.state = {
      hasNoVenue: false
    }
  }

  componentDidMount () {
    const {
      uniqueVenue,
      user
    } = this.props
    user && this.handleRequestData()
    if (uniqueVenue) {
      this.handleMergeForm()
    }
  }

  componentDidUpdate (prevProps) {
    const {
      uniqueVenue,
      user
    } = this.props
    if (prevProps.user !== user) {
      this.handleRequestData()
    }
    if (!prevProps.uniqueVenue && uniqueVenue) {
      this.handleMergeForm()
    }
  }

  handleMergeForm = () => {
    const {
      mergeForm,
      occasionId,
      uniqueVenue
    } = this.props
    mergeForm('occasions', occasionId, 'venueId', uniqueVenue.id)
  }

  handleRequestData = () => {
    const {
      history,
      requestData,
      showModal
    } = this.props
    requestData(
      'GET',
      'offerers',
      {
        handleSuccess: (state, action) => !get(state, 'data.venues.length')
          && showModal(
            <div>
              Vous devez avoir déjà enregistré un lieu
              dans une de vos structures pour ajouter des offres
            </div>,
            {
              onCloseClick: () => history.push('/structures')
            }
          ),
        normalizer: { managedVenues: 'venues' }
      }
    )
    requestData('GET', 'eventTypes')
  }

  handleShowOccurencesModal = () => {
    const {
      eventOccurences,
      showModal
    } = this.props
    showModal(
      <OccurenceManager occurences={eventOccurences} />
    )
  }

  handleSuccessData = (state, action) => {
    const {
      data,
      method
    } = action
    const {
      eventOccurences,
      history,
      match: { params: { occasionPath } },
      showModal,
      showNotification
    } = this.props

    // PATCH
    if (method === 'PATCH') {
      history.push('/offres')
      showNotification({
        text: 'Votre offre a bien été enregistrée',
        type: 'success'
      })
      return
    }

    // POST
    if (method === 'POST') {
      // switch to the path with the new created id
      history.push(`/offres/${occasionPath}/${data.id}`)

      // modal
      showModal(
        <div>
          Cette offre est-elle soumise à des dates ou des horaires particuliers ?
          <button
            className='button'
            onClick={this.handleShowOccurencesModal}
          >
            Oui
          </button>
          <button
            className='button'
            onClick={() => history.push('/offres')}
          >
            Non
          </button>
        </div>
      )
    }
  }

  render () {
    const {
      apiPath,
      eventOccurences,
      eventTypes,
      isLoading,
      isNew,
      newMediationRoutePath,
      occasionCollection,
      occasion,
      occasionIdOrNew,
      offererOptions,
      selectedOffererId,
      selectedVenueId,
      selectedVenues,
      showModal,
      user,
      venueOptions
    } = this.props
    const {
      author,
      contactName,
      contactEmail,
      contactPhone,
      description,
      durationMinutes,
      mediaUrls,
      name,
      performer,
      stageDirector,
      type,
    } = (occasion || {})

    return (
      <PageWrapper
        backTo={{path: '/offres', label: 'Vos offres'}}
        name='offer'
        loading={isLoading}
      >
        <div className='section'>
          <h1 className='pc-title'>
            {
              isNew
                ? 'Ajouter'
                : 'Modifier'
            } une offre
          </h1>
          <p className='subtitle'>
            Renseignez les détails de cette offre et mettez-la en avant en ajoutant une ou plusieurs accorches.
          </p>
          <FormField
            collectionName='occasions'
            defaultValue={name}
            entityId={occasionIdOrNew}
            label={<Label title="Titre :" />}
            name="name"
            required
            isHorizontal
            isExpanded
          />
          { !isNew && (
            <div>
              {
                occasionCollection === 'events' && (
                  <button
                    className='button'
                    onClick={this.handleShowOccurencesModal}
                  >
                    Gérer les dates
                  </button>
                )
              }
              <div className='box content has-text-centered'>
                <ReactMarkdown source={mediationExplanation} className='section' />
                <ul className='mediations-list'>
                  {get(occasion, 'mediations', []).map(m => (
                    <li>
                      <img
                        alt={`accroche-${m.thumbPath}`}
                        src={`${API_URL}${m.thumbPath}`} />
                    </li>
                  ))}
                </ul>
                <p>
                  <NavLink
                    className={`button is-primary ${get(occasion, 'mediations', []).length > 0 ? 'is-outlined' : ''}`}
                    to={newMediationRoutePath}>
                    {false && <Icon svg='ico-stars' />}
                    Ajouter une accroche
                  </NavLink>
                </p>
              </div>
            </div>
          )}
          <h2 className='pc-list-title'>Infos pratiques</h2>
          <FormField
            collectionName='occasions'
            defaultValue={type || get(eventTypes, '0.value')}
            entityId={occasionIdOrNew}
            label={<Label title="Type :" />}
            name="type"
            required
            type="select"
            options={eventTypes}
            isHorizontal
          />
          <FormField
            collectionName='occasions'
            defaultValue={selectedOffererId}
            entityId={occasionIdOrNew}
            isHorizontal
            label={<Label title="Structure :" />}
            readOnly={!isNew}
            required
            name='offererId'
            options={offererOptions}
            type="select"
          />
          {
            selectedVenues && selectedVenues.length > 1 && (
              <FormField
                collectionName='occasions'
                defaultValue={selectedVenueId}
                entityId={occasionIdOrNew}
                label={<Label title="Lieu :" />}
                name='venueId'
                readOnly={!isNew}
                required
                options={venueOptions}
                type="select"
                isHorizontal
              />
            )
          }
          {occasionCollection === 'events' && (
            <FormField
              collectionName='occasions'
              defaultValue={durationMinutes}
              entityId={occasionIdOrNew}
              label={<Label title="Durée (en minutes) :" />}
              name="durationMinutes"
              required
              type="number"
              isHorizontal
            />
          )}
          <h2 className='pc-list-title'>Infos artistiques</h2>
          <FormField
            collectionName='occasions'
            defaultValue={description}
            entityId={occasionIdOrNew}
            label={<Label title="Description :" />}
            name="description"
            required
            type="textarea"
            isHorizontal
            isExpanded
          />
          <FormField
            collectionName='occasions'
            defaultValue={author}
            entityId={occasionIdOrNew}
            label={<Label title="Auteur :" />}
            name="author"
            isHorizontal
            isExpanded
          />
          {
            occasionCollection === 'events' && [
              <FormField
                collectionName='occasions'
                defaultValue={stageDirector}
                entityId={occasionIdOrNew}
                key={0}
                label={<Label title="Metteur en scène:" />}
                name="stageDirector"
                isHorizontal
                isExpanded
              />,
              <FormField
                collectionName='occasions'
                defaultValue={performer}
                entityId={occasionIdOrNew}
                key={1}
                label={<Label title="Interprète:" />}
                name="performer"
                isHorizontal
                isExpanded
              />
            ]
          }
          <h2 className='pc-list-title'>Contact</h2>
          <FormField
            collectionName='occasions'
            defaultValue={contactName || get(user, 'publicName')}
            entityId={occasionIdOrNew}
            label={<Label title="Nom du contact :" />}
            name="contactName"
            required
            isHorizontal
            isExpanded
          />
          <FormField
            collectionName='occasions'
            defaultValue={contactEmail || get(user, 'email')}
            entityId={occasionIdOrNew}
            label={<Label title="Email de contact :" />}
            name="contactEmail"
            required
            type="email"
            isHorizontal
            isExpanded
          />
          <FormField
            collectionName='occasions'
            defaultValue={contactPhone}
            entityId={occasionIdOrNew}
            label={<Label title="Tel de contact :" />}
            name="contactPhone"
            isHorizontal
          />
          {false && <FormField
                      collectionName='occasions'
                      defaultValue={mediaUrls}
                      entityId={occasionIdOrNew}
                      label={<Label title="Media URLs" />}
                      name="mediaUrls"
                      type="list"
                    />}
          <hr />
          <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
            <div className="control">
              <NavLink to='/offres'
                className="button is-primary is-outlined is-medium">
                Retour
              </NavLink>
            </div>
            <div className="control">
              <SubmitButton
                className="button is-primary is-medium"
                getBody={form => get(form, `occasionsById.${occasionIdOrNew}`)}
                getIsDisabled={form => {
                  const missingFields = requiredFields.filter(r =>
                    !get(form, `occasionsById.${occasionIdOrNew}.${r}`));
                  return missingFields.length > 0
                }}
                handleSuccess={this.handleSuccessData}
                method={isNew ? 'POST' : 'PATCH'}
                path={apiPath}
                storeKey="occasions"
                text="Enregistrer"
              />
            </div>
          </div>
        </div>
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  withCurrentOccasion,
  connect(
    (state, ownProps) => ({
      eventOccurences: selectEventOccurences(state, ownProps),
      eventTypes: state.data.eventTypes,
      offererOptions: selectOffererOptions(state),
      selectedOffererId: selectSelectedOffererId(state, ownProps),
      selectedVenueId: selectSelectedVenueId(state, ownProps),
      selectedVenues: selectSelectedVenues(state, ownProps),
      venueOptions: selectVenueOptions(state, ownProps)
    }),
    {
      mergeForm,
      resetForm,
      showModal,
      showNotification
    }
  )
)(OfferPage)
