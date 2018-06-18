import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import MediationManager from '../MediationManager'
import OccurenceManager from '../OccurenceManager'
import withLogin from '../hocs/withLogin'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { mergeForm, resetForm } from '../../reducers/form'
import { showModal } from '../../reducers/modal'
import { showNotification } from '../../reducers/notification'
import selectOfferForm from '../../selectors/offerForm'
import selectOffererOptions from '../../selectors/offererOptions'
import selectSelectedVenueId from '../../selectors/selectedVenueId'
import selectSelectedVenues from '../../selectors/selectedVenues'
import selectVenueOptions from '../../selectors/venueOptions'



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
    requestData('GET', 'types')
  }

  handleShowOccurencesModal = () => {
    this.props.showModal(<OccurenceManager {...this.props} />)
  }

  handleSuccessData = (state, action) => {
    const {
      data,
      method
    } = action
    const {
      history,
      match: { params: { occasionPath } },
      offerForm,
      showModal,
      showNotification
    } = this.props
    const {
      isEventType
    } = (offerForm || {})

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
      /*
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
      */
      isEventType && this.handleShowOccurencesModal()
    }
  }

  render () {
    const {
      apiPath,
      currentOccasion,
      isLoading,
      isNew,
      occasionCollection,
      occasionIdOrNew,
      offerForm,
      offererOptions,
      routePath,
      selectedVenueId,
      selectedVenues,
      typeOptions,
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
      eventType,
      id,
      mediaUrls,
      mediations,
      name,
      performer,
      offererId,
      stageDirector,
      type,
    } = (currentOccasion || {})
    const {
      isEventType,
      requiredFields
    } = (offerForm || {})

    const offererOptionsWithPlaceholder = get(offererOptions, 'length') > 1
      ? [{ label: 'Sélectionnez une structure' }].concat(offererOptions)
      : offererOptions

    console.log('ET LA', this.props)


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
            isHorizontal
            isExpanded
            label={<Label title="Titre :" />}
            name="name"
            required
          />
          { !isNew && (
            <div>
              {
                isEventType && (
                  <button
                    className='button'
                    onClick={this.handleShowOccurencesModal}
                  >
                    Gérer les dates
                  </button>
                )
              }
              <MediationManager
                mediations={mediations}
              />
            </div>
          )}
          <h2 className='pc-list-title'>Infos pratiques</h2>
          <FormField
            collectionName='occasions'
            defaultValue={offererId}
            entityId={occasionIdOrNew}
            isHorizontal
            label={<Label title="Structure :" />}
            readOnly={!isNew}
            required
            name='offererId'
            options={offererOptionsWithPlaceholder}
            type="select"
          />
          {
            selectedVenues && selectedVenues.length > 1 && (
              <FormField
                collectionName='occasions'
                defaultValue={selectedVenueId}
                entityId={occasionIdOrNew}
                isHorizontal
                label={<Label title="Lieu :" />}
                name='venueId'
                options={venueOptions}
                readOnly={!isNew}
                required
                type="select"
              />
            )
          }
          <FormField
            collectionName='occasions'
            defaultValue={type}
            entityId={occasionIdOrNew}
            isHorizontal
            label={<Label title="Type :" />}
            name="type"
            options={typeOptions}
            required
            type="select"
          />
          {
            isEventType && (
              <FormField
                collectionName='occasions'
                defaultValue={durationMinutes}
                entityId={occasionIdOrNew}
                isHorizontal
                label={<Label title="Durée (en minutes) :" />}
                name="durationMinutes"
                required
                type="number"
              />
            )
          }
          <h2 className='pc-list-title'>Infos artistiques</h2>
          <FormField
            collectionName='occasions'
            defaultValue={description}
            entityId={occasionIdOrNew}
            isHorizontal
            isExpanded
            label={<Label title="Description :" />}
            name="description"
            type="textarea"
            required
          />
          <FormField
            collectionName='occasions'
            defaultValue={author}
            entityId={occasionIdOrNew}
            isHorizontal
            isExpanded
            label={<Label title="Auteur :" />}
            name="author"
          />
          {
            isEventType && [
              <FormField
                collectionName='occasions'
                defaultValue={stageDirector}
                entityId={occasionIdOrNew}
                isHorizontal
                isExpanded
                key={0}
                label={<Label title="Metteur en scène:" />}
                name="stageDirector"
              />,
              <FormField
                collectionName='occasions'
                defaultValue={performer}
                entityId={occasionIdOrNew}
                isHorizontal
                isExpanded
                key={1}
                label={<Label title="Interprète:" />}
                name="performer"
              />
            ]
          }
          <h2 className='pc-list-title'>Contact</h2>
          <FormField
            collectionName='occasions'
            defaultValue={contactName || get(user, 'publicName')}
            entityId={occasionIdOrNew}
            isHorizontal
            isExpanded
            label={<Label title="Nom du contact :" />}
            name="contactName"
            required
          />
          <FormField
            collectionName='occasions'
            defaultValue={contactEmail || get(user, 'email')}
            entityId={occasionIdOrNew}
            isHorizontal
            isExpanded
            label={<Label title="Email de contact :" />}
            name="contactEmail"
            required
            type="email"
          />
          <FormField
            collectionName='occasions'
            defaultValue={contactPhone}
            entityId={occasionIdOrNew}
            isHorizontal
            label={<Label title="Tel de contact :" />}
            name="contactPhone"
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
                  if (!requiredFields) {
                    return true
                  }
                  const missingFields = requiredFields.filter(r =>
                    !get(form, `occasionsById.${occasionIdOrNew}.${r}`))
                  return isNew
                    ? missingFields.length > 0
                    : missingFields.length === requiredFields.length
                }}
                handleSuccess={this.handleSuccessData}
                method={isNew ? 'POST' : 'PATCH'}
                path={eventType
                  ? `events${id ? `/${id}` : ''}`
                  : `things${id ? `/${id}` : ''}`
                }
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
      offerForm: selectOfferForm(state, ownProps),
      offererOptions: selectOffererOptions(state, ownProps),
      selectedVenueId: selectSelectedVenueId(state, ownProps),
      selectedVenues: selectSelectedVenues(state, ownProps),
      typeOptions: state.data.types,
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
