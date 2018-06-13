import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'


import OccurenceManager from '../OccurenceManager'
import withLogin from '../hocs/withLogin'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { mergeForm, resetForm } from '../../reducers/form'
import { showModal } from '../../reducers/modal'
import { SUCCESS } from '../../reducers/queries'
import selectOfferers from '../../selectors/offerers'
import selectFormOfferer from '../../selectors/formOfferer'
import selectOffererOptions from '../../selectors/offererOptions'
import selectUniqueVenue from '../../selectors/uniqueVenue'
import selectVenueOptions from '../../selectors/venueOptions'
import { pathToCollection } from '../../utils/translate'


class OfferPage extends Component {
  constructor () {
    super()
    this.state = {
      defaultOfferer: null
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
    if (prevProps.user !== this.props.user) {
      this.handleRequestData()
    }
    if (!prevProps.uniqueVenue && this.props.uniqueVenue) {
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
    const { requestData } = this.props
    requestData(
      'GET',
      'offerers',
      {
        normalizer: { managedVenues: 'venues' }
      }
    )
    requestData('GET', 'eventTypes')
  }

  handleStatusData = status => {
    const {
      history,
      resetForm
    } = this.props
    if (status === SUCCESS) {
      history.push('/offres?success=true')
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      formOfferer,
      occurences
    } = nextProps
    const defaultOfferer = get(occurences, '0.offer.0.offerer')
    const offerer = formOfferer || defaultOfferer
    return {
      defaultOfferer
    }
  }

  render () {
    const {
      apiPath,
      eventTypes,
      isLoading,
      isNew,
      occasionCollection,
      occasion,
      occasionId,
      offererOptions,
      offerers,
      uniqueVenue,
      user,
      venueOptions
    } = this.props
    const {
      author,
      bookingLimitDatetime,
      contactName,
      contactEmail,
      contactPhone,
      description,
      durationMinutes,
      mediaUrls,
      name,
      performer,
      stageDirector,
      occurences,
      type,
    } = (occasion || {})
    const {
      defaultOfferer
    } = this.state

    return (
      <PageWrapper name='offer' loading={isLoading}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink to='/offres' className="button is-primary is-outlined">
                Retour
              </NavLink>
            </div>
            <h1 className='title has-text-centered'>
              {
                isNew
                  ? 'Créer'
                  : 'Modifier'
              } {
                occasionCollection === 'events'
                  ? 'un événement'
                  : 'un objet'
                }
            </h1>
            <FormField
              collectionName='occasions'
              defaultValue={name}
              entityId={occasionId}
              label={<Label title="Titre :" />}
              name="name"
              required
            />
            <hr />
            <h2 className='subtitle is-2'>
              Infos pratiques
            </h2>
            <FormField
              collectionName='occasions'
              defaultValue={type || get(eventTypes, '0.value')}
              entityId={occasionId}
              label={<Label title="Type :" />}
              name="type"
              required
              type="select"
              options={eventTypes}
            />
            <FormField
              collectionName='occasions'
              defaultValue={defaultOfferer || get(offerers, '0.id')}
              entityId={occasionId}
              label={<Label title="Structure :" />}
              readOnly={!isNew}
              required
              name='offererId'
              options={offererOptions}
              type="select"
            />
            {
              !uniqueVenue && (
                <FormField
                  collectionName='events'
                  defaultValue={
                    get(occurences, '0.venue.id') ||
                    get(venueOptions, '0.value')
                  }
                  entityId={occasionId}
                  label={<Label title="Lieu" />}
                  name='venueId'
                  readOnly={!isNew}
                  required
                  options={venueOptions}
                  type="select"
                />
              )
            }
            {
              occasionCollection === 'events' && [
                <div className='field' key={1}>
                  <Label title='Horaires :' />
                  <OccurenceManager occurences={occurences} />
                </div>,
                <FormField
                  collectionName='occasions'
                  defaultValue={durationMinutes}
                  entityId={occasionId}
                  key={2}
                  label={<Label title="Durée (en minutes) :" />}
                  name="durationMinutes"
                  required
                  type="number"
                />,
                <FormField
                  collectionName='occasions'
                  defaultValue={bookingLimitDatetime}
                  entityId={occasionId}
                  key={3}
                  label={<Label title="Date limite d'inscription (par défaut: 48h avant l'événement)" />}
                  name="bookingLimitDatetime"
                  type="date"
                />
              ]
            }
            <hr />
            <h2 className='subtitle is-2'>Infos artistiques</h2>
            <FormField
              collectionName='occasions'
              defaultValue={description}
              entityId={occasionId}
              label={<Label title="Description :" />}
              name="description"
              required
              type="textarea"
            />
            <FormField
              collectionName='occasions'
              defaultValue={author}
              entityId={occasionId}
              label={<Label title="Auteur :" />}
              name="author"
            />
            {
              occasionCollection === 'events' && [
                <FormField
                  collectionName='occasions'
                  defaultValue={stageDirector}
                  entityId={occasionId}
                  key={0}
                  label={<Label title="Metteur en scène:" />}
                  name="stageDirector"
                />,
                <FormField
                  collectionName='occasions'
                  defaultValue={performer}
                  entityId={occasionId}
                  key={1}
                  label={<Label title="Interprète:" />}
                  name="performer"
                />
              ]
            }
            <hr />
            <h2 className='subtitle is-2'>Infos de contact</h2>
            <FormField
              collectionName='occasions'
              defaultValue={contactName}
              entityId={occasionId}
              label={<Label title="Nom du contact :" />}
              name="contactName"
            />
            <FormField
              collectionName='occasions'
              defaultValue={contactEmail}
              entityId={occasionId}
              label={<Label title="Email de contact :" />}
              name="contactEmail"
              required
              type="email"
            />
            <FormField
              collectionName='occasions'
              defaultValue={contactPhone}
              entityId={occasionId}
              label={<Label title="Tel de contact :" />}
              name="contactPhone"
            />
            <FormField
              collectionName='occasions'
              defaultValue={mediaUrls}
              entityId={occasionId}
              label={<Label title="Media URLs" />}
              name="mediaUrls"
              type="list"
            />
            <hr />
            <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
              <div className="control">
                <SubmitButton
                  getBody={form => ({
                    occasion: get(form, `occasionsById.${occasionId}`),
                    eventOccurences: form.eventOccurencesById &&
                      Object.values(form.eventOccurencesById)
                  })}
                  getIsDisabled={form => {
                    return isNew
                    ? !get(form, `occasionsById.${occasionId}.contactEmail`) ||
                      !get(form, `occasionsById.${occasionId}.description`) ||
                      !get(form, `occasionsById.${occasionId}.durationMinutes`) ||
                      !get(form, `occasionsById.${occasionId}.name`) ||
                      !get(form, `occasionsById.${occasionId}.offererId`) ||
                      typeof get(form, `occasionsById.${occasionId}.type`) !== 'string' ||
                      (!form.eventOccurencesById || !Object.keys(form.eventOccurencesById).length)
                    : !get(form, `occasionsById.${occasionId}.contactEmail`) &&
                      !get(form, `occasionsById.${occasionId}.description`) &&
                      !get(form, `occasionsById.${occasionId}.durationMinutes`) &&
                      !get(form, `occasionsById.${occasionId}.name`) &&
                      !get(form, `occasionsById.${occasionId}.offererId`) &&
                      typeof get(form, `occasionsById.${occasionId}.type`) !== 'string' &&
                      (!form.eventOccurencesById || !Object.keys(form.eventOccurencesById).length)
                  }}
                  className="button is-primary is-medium"
                  method={isNew ? 'POST' : 'PATCH'}
                  handleStatusChange={status => this.handleStatusData(status)}
                  path={apiPath}
                  storeKey="occasions"
                  text="Enregistrer"
                />
              </div>
              <div className="control">
                <NavLink to='/offres'
                  className="button is-primary is-outlined is-medium">
                  Retour
                </NavLink>
              </div>
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
      eventTypes: state.data.eventTypes,
      formOfferer: selectFormOfferer(state, ownProps),
      offerers: selectOfferers(state),
      offererOptions: selectOffererOptions(state),
      uniqueVenue: selectUniqueVenue(state, ownProps),
      venueOptions: selectVenueOptions(state, ownProps)
    }),
    { mergeForm, resetForm }
  )
)(OfferPage)
