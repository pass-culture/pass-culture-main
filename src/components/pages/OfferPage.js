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
import { resetForm } from '../../reducers/form'
import { showModal } from '../../reducers/modal'
import selectFormOfferer from '../../selectors/formOfferer'
import selectOffererOptions from '../../selectors/offererOptions'
import { pathToCollection } from '../../utils/translate'


class OfferPage extends Component {
  constructor () {
    super()
    this.state = {
      defaultOfferer: null
    }
  }

  componentDidMount() {
    this.props.requestData('GET', 'eventTypes')
  }

  onSubmitClick = () => {
    const {
      history,
      resetForm,
      showModal
    } = this.props
    resetForm()
    showModal(
      <div>
        C'est soumis!
      </div>,
      {
        onCloseClick: () => history.push('/offres')
      }
    )
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      formOfferer,
      occurences
    } = nextProps
    const defaultOfferer = get(occurences, '0.offer.0.offerer')
    const offerer = formOfferer || defaultOfferer
    const venueOptions = offerer &&
      offerer.managedVenues &&
      offerer.managedVenues.map(v => ({
        label: v.name,
        value: v.id
      }))
    return {
      defaultOfferer,
      venueOptions
    }
  }

  render () {
    const {
      apiPath,
      author,
      bookingLimitDatetime,
      contactName,
      contactEmail,
      contactPhone,
      description,
      durationMinutes,
      eventTypes,
      isLoading,
      isNew,
      mediaUrls,
      name,
      occasionCollection,
      occasionId,
      occurences,
      offererOptions,
      performer,
      stageDirector,
      type,
      user
    } = this.props
    const {
      defaultOfferer,
      venueOptions
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
              collectionName={occasionCollection}
              defaultValue={name}
              entityId={occasionId}
              label={<Label title="Titre" />}
              name="name"
              required
            />
            <hr />
            <h2 className='subtitle is-2'>
              Infos pratiques
            </h2>
            <FormField
              collectionName={occasionCollection}
              defaultValue={type || ''}
              entityId={occasionId}
              label={<Label title="Type" />}
              name="type"
              type="select"
              options={eventTypes}
            />
            <FormField
              collectionName={occasionCollection}
              defaultValue={defaultOfferer}
              entityId={occasionId}
              label={<Label title="Structure" />}
              name='offererId'
              options={offererOptions}
              type="select"
            />
            {
              venueOptions && venueOptions.length > 1 && (
                <FormField
                  collectionName='events'
                  defaultValue={get(occurences, '0.venue')}
                  entityId={occasionId}
                  label={<Label title="Lieu" />}
                  name='venueId'
                  options={venueOptions}
                  type="select"
                />
              )
            }
            {
              occasionCollection === 'events' && [
                null && <FormField
                  collectionName='venues'
                  defaultValue={get(occurences, '0.venue')}
                  ItemComponent={({ address, name, onItemClick }) => (
                    <div className='venue-item' onClick={onItemClick}>
                      <b> {name} </b> {address}
                    </div>
                  )}
                  key={0}
                  label={<Label title="Lieu" />}
                  type="select"
                />,
                <div className='field' key={1}>
                  <Label title='Horaires' />
                  <OccurenceManager occurences={occurences} />
                </div>,
                <FormField
                  collectionName={occasionCollection}
                  defaultValue={durationMinutes}
                  entityId={occasionId}
                  key={2}
                  label={<Label title="Durée (en minutes)" />}
                  name="durationMinutes"
                  required
                  type="number"
                />,
                <FormField
                  collectionName={occasionCollection}
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
              collectionName={occasionCollection}
              defaultValue={description}
              entityId={occasionId}
              label={<Label title="Description" />}
              name="description"
              required
              type="textarea"
            />
            <FormField
              collectionName={occasionCollection}
              defaultValue={author}
              entityId={occasionId}
              label={<Label title="Auteur" />}
              name="author"
            />
            {
              occasionCollection === 'events' && [
                <FormField
                  collectionName={occasionCollection}
                  defaultValue={stageDirector}
                  entityId={occasionId}
                  key={0}
                  label={<Label title="Metteur en scène" />}
                  name="stageDirector"
                />,
                <FormField
                  collectionName={occasionCollection}
                  defaultValue={performer}
                  entityId={occasionId}
                  key={1}
                  label={<Label title="Interprète" />}
                  name="performer"
                />
              ]
            }
            <hr />
            <h2 className='subtitle is-2'>Infos de contact</h2>
            <FormField
              collectionName={occasionCollection}
              defaultValue={contactName}
              entityId={occasionId}
              label={<Label title="Nom du contact" />}
              name="contactName"
            />
            <FormField
              collectionName={occasionCollection}
              defaultValue={contactEmail}
              entityId={occasionId}
              label={<Label title="Email de contact" />}
              name="contactEmail"
              required
              type="email"
            />
            <FormField
              collectionName={occasionCollection}
              defaultValue={contactPhone}
              entityId={occasionId}
              label={<Label title="Tel de contact" />}
              name="contactPhone"
            />
            <FormField
              collectionName={occasionCollection}
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
                    occasion: get(form, `${occasionCollection}ById.${occasionId}`),
                    eventOccurences: form.eventOccurencesById &&
                      Object.values(form.eventOccurencesById),
                    //offererId: get(form, `offerersById.${SEARCH}.id`),
                    //venueId: get(form, `venuesById.${SEARCH}.id`)
                  })}
                  getIsDisabled={form => {
                    //const offererId = get(form, `offerersById.${SEARCH}.id`)
                    //const venueId = get(form, `venuesById.${SEARCH}.id`)
                    //if (!offererId || !venueId) {
                    //  return true
                    //}
                    return isNew
                    ? !get(form, `${occasionCollection}ById.${occasionId}.description`) ||
                      !get(form, `${occasionCollection}ById.${occasionId}.name`) ||
                      !get(form, `${occasionCollection}ById.${occasionId}.mediaUrls`) ||
                      typeof get(form, `${occasionCollection}ById.${occasionId}.type`) !== 'string' ||
                      (!form.eventOccurencesById || !Object.keys(form.eventOccurencesById).length)
                    : !get(form, `${occasionCollection}ById.${occasionId}.description`) &&
                      !get(form, `${occasionCollection}ById.${occasionId}.name`) &&
                      !get(form, `${occasionCollection}ById.${occasionId}.mediaUrls`) &&
                      typeof get(form, `${occasionCollection}ById.${occasionId}.type`) !== 'string' &&
                      (!form.eventOccurencesById || !Object.keys(form.eventOccurencesById).length)
                  }}
                  className="button is-primary is-medium"
                  method={isNew ? 'POST' : 'PATCH'}
                  onClick={this.onSubmitClick}
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
      offererOptions: selectOffererOptions(state),
      formOfferer: selectFormOfferer(state, ownProps),
    }),
    { resetForm, showModal }
  )
)(OfferPage)
