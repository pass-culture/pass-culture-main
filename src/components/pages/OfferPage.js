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
import Icon from '../layout/Icon'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { mergeForm, resetForm } from '../../reducers/form'
import { showModal } from '../../reducers/modal'
import { showNotification } from '../../reducers/notification'
import selectOfferForm from '../../selectors/offerForm'
import selectOffererOptions from '../../selectors/offererOptions'
import selectSelectedOffererId from '../../selectors/selectedOffererId'
import selectSelectedVenueId from '../../selectors/selectedVenueId'
import selectSelectedVenues from '../../selectors/selectedVenues'
import selectVenueOptions from '../../selectors/venueOptions'

import { pluralize } from '../../utils/string'

class OfferPage extends Component {
  constructor () {
    super()
    this.state = {
      isReadOnly: true,
      hasNoVenue: false
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      location: { search },
      isNew
    } = nextProps
    const isEdit = search === '?modifie'
    const isReadOnly = !isNew && !isEdit
    return {
      isReadOnly
    }
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
    const {
      currentOccasion,
      selectedVenueId,
      showModal
    } = this.props
    const {
      occurences
    } = (currentOccasion || {})
    showModal(
      selectedVenueId
        ? <OccurenceManager {...this.props} />
        : (
          <div>
            Vous devez déjà avoir sélectionné une structure et un lieu
            responsable pour gérer des dates
          </div>
        )
    )
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
      const routePath = `/offres/${isEventType ? 'evenements' : 'objets'}/${data.id}`
      history.push(routePath)

      // modal
      isEventType && showModal(
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

  componentWillUnmount () {
    console.log('OUEI')
  }

  handleMergeForm = () => {
    const {
      mergeForm,
      occasionId,
      uniqueVenue
    } = this.props
    mergeForm('occasions', occasionId, 'venueId', uniqueVenue.id)
  }

  render () {
    const {
      apiPath,
      currentOccasion,
      isLoading,
      isNew,
      location: { pathname },
      occasionCollection,
      occasionIdOrNew,
      offerForm,
      offererOptions,
      routePath,
      selectedOffererId,
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
      id,
      mediaUrls,
      mediations,
      name,
      performer,
      occurences,
      stageDirector,
      typeOption,
    } = (currentOccasion || {})
    const {
      isEventType,
      requiredFields
    } = (offerForm || {})
    const {
      isReadOnly
    } = this.state
    const typeOptionsWithPlaceholder = get(typeOptions, 'length') > 1
      ? [{ label: "Sélectionnez un type d'offre" }].concat(typeOptions)
      : typeOptions

    const offererOptionsWithPlaceholder = get(offererOptions, 'length') > 1
      ? [{ label: 'Sélectionnez une structure' }].concat(offererOptions)
      : offererOptions

    const venueOptionsWithPlaceholder = get(venueOptions, 'length') > 1
      ? [{ label: 'Sélectionnez un lieu' }].concat(venueOptions)
      : venueOptions

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
            label={<Label title="Titre de l'offre:" />}
            name="name"
            readOnly={isReadOnly}
            required={!isReadOnly}
          />
          { !isNew && (
            <div className='field'>
              {
                isEventType && (
                  <div className='field form-field is-horizontal'>
                    <div className='field-label'>
                      <label className="label" htmlFor="input_occasions_name">
                        <div className="subtitle">Dates :</div>
                      </label>
                    </div>
                    <div className='field-body'>
                      <div className='field'>
                        <div className='nb-dates'>
                          {pluralize(occurences.length, 'date')}
                        </div>
                        <button
                          className='button is-primary is-outlined is-small'
                          onClick={this.handleShowOccurencesModal}
                        >
                          <span className='icon'><Icon svg='ico-calendar' /></span>
                          <span>Gérer les dates</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )
              }
              <MediationManager
                mediations={mediations}
              />
            </div>
          )}
          <h2 className='pc-list-title'>Infos pratiques</h2>
          {
            /*
            <FormField
              collectionName='occasions'
              entityId={occasionIdOrNew}
              isHorizontal
              label={<Label title="Prix:" />}
              name="price"
              readOnly={isReadOnly}
            />
            <FormField
              className='column'
              collectionName='occasions'
              entityId={occasionIdOrNew}
              inputClassName='input is-rounded'
              label={<Label title="Gratuit" />}
              name="isForFree"
              readOnly={isReadOnly}
              type="checkbox"
            />
            */
          }
          <FormField
            collectionName='occasions'
            defaultValue={selectedOffererId}
            entityId={occasionIdOrNew}
            isHorizontal
            label={<Label title="Structure :" />}
            readOnly={!isNew}
            required
            name='offererId'
            options={offererOptionsWithPlaceholder}
            readOnly={isReadOnly}
            type="select"
          />
          {
            selectedOffererId && get(venueOptions, 'length') === 0
              ? (
                <p>
                  Il faut obligatoirement une structure avec un lieu.
                </p>
              )
              :
                get(venueOptions, 'length') > 0 && <FormField
                  collectionName='occasions'
                  defaultValue={selectedVenueId}
                  entityId={occasionIdOrNew}
                  isHorizontal
                  label={<Label title="Lieu :" />}
                  name='venueId'
                  options={venueOptionsWithPlaceholder}
                  readOnly={!isNew}
                  readOnly={isReadOnly}
                  required={!isReadOnly}
                  type="select"
                />
          }
          <FormField
            collectionName='occasions'
            defaultValue={get(typeOption, 'value')}
            entityId={occasionIdOrNew}
            isHorizontal
            label={<Label title="Type :" />}
            name="type"
            options={typeOptionsWithPlaceholder}
            readOnly={isReadOnly}
            required={!isReadOnly}
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
                readOnly={isReadOnly}
                required={!isReadOnly}
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
            readOnly={isReadOnly}
            required={!isReadOnly}
            type="textarea"
          />
          <FormField
            collectionName='occasions'
            defaultValue={author}
            entityId={occasionIdOrNew}
            isHorizontal
            isExpanded
            label={<Label title="Auteur :" />}
            name="author"
            readOnly={isReadOnly}
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
                readOnly={isReadOnly}
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
                readOnly={isReadOnly}
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
            readOnly={isReadOnly}
            required={!isReadOnly}
          />
          <FormField
            collectionName='occasions'
            defaultValue={contactEmail || get(user, 'email')}
            entityId={occasionIdOrNew}
            isHorizontal
            isExpanded
            label={<Label title="Email de contact :" />}
            name="contactEmail"
            readOnly={isReadOnly}
            required={!isReadOnly}
            type="email"
          />
          <FormField
            collectionName='occasions'
            defaultValue={contactPhone}
            entityId={occasionIdOrNew}
            isHorizontal
            label={<Label title="Tel de contact :" />}
            name="contactPhone"
            readOnly={isReadOnly}
          />
          {false && <FormField
                      collectionName='occasions'
                      defaultValue={mediaUrls}
                      entityId={occasionIdOrNew}
                      label={<Label title="Media URLs" />}
                      name="mediaUrls"
                      readOnly={isReadOnly}
                      type="list"
                    />}
          <hr />
          <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
            <div className="control">
              {
                isReadOnly
                  ? (
                    <NavLink to={`${pathname}?modifie`} className='button is-secondary is-medium'>
                      Modifier l'offre
                    </NavLink>
                  )
                  : (
                    <NavLink
                      className="button is-secondary is-medium"
                      to='/offres'>
                      Annuler
                    </NavLink>
                  )
              }
            </div>
            <div className="control">
              {
                isReadOnly
                  ? (
                    <NavLink to={routePath} className='button is-primary is-medium'>
                      Terminer
                    </NavLink>
                  )
                  : (
                    <SubmitButton
                      className="button is-primary is-medium"
                      getBody={form => {
                        const occasionForm = get(form, `occasionsById.${occasionIdOrNew}`)
                        // remove the EventType. ThingType.
                        if (occasionForm.type) {
                          occasionForm.type = occasionForm.type.split('.')[1]
                        }
                        return occasionForm
                      }}
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
                      path={isEventType
                        ? `events${id ? `/${id}` : ''}`
                        : `things${id ? `/${id}` : ''}`
                      }
                      storeKey="occasions"
                      text="Enregistrer"
                    />
                  )
                }
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
      selectedOffererId: selectSelectedOffererId(state, ownProps),
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
