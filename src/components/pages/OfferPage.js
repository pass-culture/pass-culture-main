import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'


import OccurenceManager from '../OccurenceManager'
import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import Label from '../layout/Label'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { requestData } from '../../reducers/data'
import { resetForm } from '../../reducers/form'
import { showModal } from '../../reducers/modal'
import selectCurrentOccasion from '../../selectors/currentOccasion'
import selectOccasionPath from '../../selectors/occasionPath'
import { SEARCH } from '../../utils/config'
import { pathToCollection} from '../../utils/translate'


class OfferPage extends Component {

  handleRequestData = () => {
    const {
      occasionPath,
      occasionId,
      requestData,
    } = this.props
    occasionId !== 'nouveau' && requestData(
      'GET',
      `occasions/${pathToCollection(occasionPath)}/${occasionId}`,
      { key: 'occasions' }
    )
  }

  componentDidMount() {
    this.handleRequestData()
    this.props.requestData('GET', 'eventTypes')
  }

  componentDidUpdate(prevProps) {
    const { occasion, occasionId } = this.props
    if (!occasion && occasionId !== prevProps.occasionId) {
      this.handleRequestData()
    }
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

  render () {
    const {
      isNew,
      eventTypes,
      occasion,
      occasionId,
      occasionPath,
      path,
    } = this.props

    const {
      id,
      name,
      performer,
      stageDirector,
      author,
      bookingLimitDatetime,
      contactName,
      contactEmail,
      contactPhone,
      description,
      durationMinutes,
      mediaUrls,
      occurences,
      type,
    } = occasion || {}
    return (
      <PageWrapper name='offer' loading={!(id || isNew)}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink to='/offres' className="button is-primary is-outlined">
                Retour
              </NavLink>
            </div>
            <h1 className='title has-text-centered'>
              {isNew ? 'Créer' : 'Modifier'} {occasionPath === 'evenements' ? 'un événement' : 'un objet'}
            </h1>
            <div className='field'>
              <NavLink to={`/offres/${occasionPath}/${occasionId}/accroches/nouveau`} className='button is-primary is-outlined'>Nouvelle accroche</NavLink>
            </div>
            <FormField
              collectionName={occasionPath}
              defaultValue={name}
              entityId={id}
              label={<Label title="Titre" />}
              name="name"
              required
            />
            <hr />
            <h2 className='subtitle is-2'>Infos pratiques</h2>
            <FormField
              collectionName={occasionPath}
              defaultValue={type || ''}
              entityId={id}
              label={<Label title="Type" />}
              name="type"
              type="select"
              options={eventTypes}
            />
            <FormField
              collectionName='offerers'
              defaultValue={get(occurences, '0.offer.0.offerer')}
              ItemComponent={({ address, name, onItemClick }) => (
                <div className='venue-item' onClick={onItemClick}>
                  <b> {name} </b> {address}
                </div>
              )}
              key={0}
              label={<Label title="Etablissement" />}
              type="search"
            />
            {
              occasionPath === 'evenements' && [
                <FormField
                  collectionName='venues'
                  defaultValue={get(occurences, '0.venue')}
                  ItemComponent={({ address, name, onItemClick }) => (
                    <div className='venue-item' onClick={onItemClick}>
                      <b> {name} </b> {address}
                    </div>
                  )}
                  key={0}
                  label={<Label title="Lieu" />}
                  type="search"
                />,
                <div className='field' key={1}>
                  <Label title='Horaires' />
                  <OccurenceManager occurences={occurences} />
                </div>,
                <FormField
                  collectionName={occasionPath}
                  defaultValue={durationMinutes}
                  entityId={id}
                  key={2}
                  label={<Label title="Durée (en minutes)" />}
                  name="durationMinutes"
                  required
                  type="number"
                />,
                <FormField
                  collectionName={occasionPath}
                  defaultValue={bookingLimitDatetime}
                  entityId={id}
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
              collectionName={occasionPath}
              defaultValue={description}
              entityId={id}
              label={<Label title="Description" />}
              name="description"
              required
              type="textarea"
            />
            <FormField
              collectionName={occasionPath}
              defaultValue={author}
              entityId={id}
              label={<Label title="Auteur" />}
              name="author"
            />
            {
              occasionPath === 'evements' && [
                <FormField
                  collectionName={occasionPath}
                  defaultValue={stageDirector}
                  entityId={id}
                  key={0}
                  label={<Label title="Metteur en scène" />}
                  name="stageDirector"
                />,
                <FormField
                  collectionName={occasionPath}
                  defaultValue={performer}
                  entityId={id}
                  key={1}
                  label={<Label title="Interprète" />}
                  name="performer"
                />
              ]
            }
            <hr />
            <h2 className='subtitle is-2'>Infos de contact</h2>
            <FormField
              collectionName={occasionPath}
              defaultValue={contactName}
              entityId={id}
              label={<Label title="Nom du contact" />}
              name="contactName"
            />
            <FormField
              collectionName={occasionPath}
              defaultValue={contactEmail}
              entityId={id}
              label={<Label title="Email de contact" />}
              name="contactEmail"
              required
              type="email"
            />
            <FormField
              collectionName={occasionPath}
              defaultValue={contactPhone}
              entityId={id}
              label={<Label title="Tel de contact" />}
              name="contactPhone"
            />
            <FormField
              collectionName={occasionPath}
              defaultValue={mediaUrls}
              entityId={id}
              label={<Label title="Media URLs" />}
              name="mediaUrls"
              type="list"
            />
            <hr />
            <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
              <div className="control">
                <SubmitButton
                  getBody={form => ({
                    occasion: get(form, `${occasionPath}ById.${occasionId}`),
                    eventOccurences: form.eventOccurencesById && Object.values(form.eventOccurencesById),
                    offererId: get(form, `offerersById.${SEARCH}.id`),
                    venueId: get(form, `venuesById.${SEARCH}.id`)
                  })}
                  getIsDisabled={form => {
                    const offererId = get(form, `offerersById.${SEARCH}.id`)
                    const venueId = get(form, `venuesById.${SEARCH}.id`)
                    if (!offererId || !venueId) {
                      return true
                    }
                    return isNew
                    ? !get(form, `${occasionPath}ById.${occasionId}.description`) ||
                      !get(form, `${occasionPath}ById.${occasionId}.name`) ||
                      !get(form, `${occasionPath}ById.${occasionId}.mediaUrls`) ||
                      typeof get(form, `${occasionPath}ById.${occasionId}.type`) !== 'string' ||
                      (!form.eventOccurencesById || !Object.keys(form.eventOccurencesById).length)
                    : !get(form, `${occasionPath}ById.${occasionId}.description`) &&
                      !get(form, `${occasionPath}ById.${occasionId}.name`) &&
                      !get(form, `${occasionPath}ById.${occasionId}.mediaUrls`) &&
                      typeof get(form, `${occasionPath}ById.${occasionId}.type`) !== 'string' &&
                      (!form.eventOccurencesById || !Object.keys(form.eventOccurencesById).length)
                  }}
                  className="button is-primary is-medium"
                  method={isNew ? 'POST' : 'PATCH'}
                  onClick={this.onSubmitClick}
                  path={path}
                  storeKey="occasions"
                  text="Enregistrer"
                />
              </div>
              <div className="control">
                <NavLink to='/offres' className="button is-primary is-outlined is-medium">Retour</NavLink>
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
  connect(
    (state, ownProps) => {
      return {
        isNew: ownProps.match.params.occasionId === 'nouveau',
        eventTypes: state.data.eventTypes,
        occasionPath: ownProps.match.params.occasionPath,
        occasionId: ownProps.match.params.occasionId,
        path: selectOccasionPath(state, ownProps),
        occasion: selectCurrentOccasion(state, ownProps),
        user: state.user,
      }
    },
    { resetForm, requestData, showModal }
  )
)(OfferPage)
