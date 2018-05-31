import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import get from 'lodash.get'
import { NavLink } from 'react-router-dom'

import OccurenceManager from '../OccurenceManager'
import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import PageWrapper from '../layout/PageWrapper'
import SubmitButton from '../layout/SubmitButton'
import { requestData } from '../../reducers/data'
import { resetForm } from '../../reducers/form'
import selectCurrentOccasion from '../../selectors/currentOccasion'
import selectCurrentPath from '../../selectors/currentPath'
import selectEventTypes from '../../selectors/eventTypes'
import { NEW } from '../../utils/config'

const Label = ({ title }) => {
  return <div className="subtitle">{title}</div>
}

class OfferPage extends Component {

  constructor() {
    super()
    this.state = {
      occasion: null,
    }
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    if (nextProps.isNew) return {occasion: {}}
    return {
      occasion: nextProps.occasion
    }
  }

  handleRequestData = () => {
    const {
      collectionName,
      occasionId,
      requestData,
    } = this.props
    occasionId !== 'nouveau' && requestData(
      'GET',
      `occasions/${collectionName}/${occasionId}`,
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

  updateOccasion = (key, value) => {
    const newValue = key.split('.').reverse().reduce((result, keyElement) => {
      return {[keyElement]: (result || value)}
    }, null)
    this.setState({
      occasion: Object.assign({}, this.state.occasion, newValue)
    })
  }

  addMediaUrl = () => {
    this.updateOccasion(
      'mediaUrls',
      Object.values(get(this.state, 'occasion.mediaUrls', [])).concat('')
    )
  }

  deleteMediaUrl = index => {
    this.updateOccasion(
      'mediaUrls',
      Object.values(get(this.state, 'occasion.mediaUrls', []))
            .filter((_, i) => index !== i)
    )
  }

  onSubmitClick = () => {
    this.props.resetForm()
  }

  render () {
    const {
      author,
      bookingLimitDatetime,
      contactName,
      contactEmail,
      contactPhone,
      description,
      durationMinutes,
      eventTypes,
      id,
      isNew,
      mediaUrls,
      name,
      occasion,
      occasionType,
      occurences,
      path,
      performer,
      stageDirector,
      type
    } = this.props
    const occasionId = isNew ? NEW : this.props.occasionId
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
              {isNew ? 'Créer' : 'Modifier'} {occasionType === 'evenements' ? 'un événement' : 'un objet'}
            </h1>
            <form>
              <FormField
                autoComplete="name"
                collectionName="events"
                defaultValue={name}
                entityId={id}
                label={<Label title="Titre" />}
                name="name"
              />
              <hr />
              <h2 className='subtitle is-2'>Infos pratiques</h2>
              <FormField
                collectionName="events"
                defaultValue={type || ''}
                entityId={id}
                label={<Label title="Type" />}
                name="type"
                type="select"
                options={eventTypes}
              />
              <div className='field'>
              <Label title='Horaires' />
                <OccurenceManager occurences={occurences} />
              </div>

              <FormField
                autoComplete="durationMinutes"
                collectionName="events"
                defaultValue={durationMinutes}
                entityId={id}
                label={<Label title="Durée (en minutes)" />}
                name="durationMinutes"
                type="number"
              />
              <FormField
                autoComplete="bookingLimitDatetimes"
                collectionName="events"
                defaultValue={bookingLimitDatetime}
                entityId={id}
                label={<Label title="Date limite d'inscription (par défaut: 48h avant l'événement)" />}
                name="bookingLimitDatetime"
                type="date"
              />

              <hr />
              <h2 className='subtitle is-2'>Infos artistiques</h2>
              <FormField
                autoComplete="description"
                collectionName="events"
                defaultValue={description}
                entityId={id}
                label={<Label title="Description" />}
                name="description"
                type="textarea"
              />
              <FormField
                autoComplete="author"
                collectionName="events"
                defaultValue={author}
                entityId={id}
                label={<Label title="Auteur" />}
                name="author"
              />
              <FormField
                autoComplete="stageDirector"
                collectionName="events"
                defaultValue={stageDirector}
                entityId={id}
                label={<Label title="Metteur en scène" />}
                name="stageDirector"
              />
              <FormField
                autoComplete="performer"
                collectionName="events"
                defaultValue={performer}
                entityId={id}
                label={<Label title="Interprète" />}
                name="performer"
              />
              <hr />
              <h2 className='subtitle is-2'>Infos de contact</h2>
              <FormField
                autoComplete="contactName"
                collectionName="events"
                defaultValue={contactName}
                entityId={id}
                label={<Label title="Nom du contact" />}
                name="contactName"
              />
              <FormField
                autoComplete="contactEmail"
                collectionName="events"
                defaultValue={contactEmail}
                entityId={id}
                label={<Label title="Email de contact" />}
                name="contactEmail"
                type="email"

              />
              <FormField
                autoComplete="contactPhone"
                collectionName="events"
                defaultValue={contactPhone}
                entityId={id}
                label={<Label title="Tel de contact" />}
                name="contactPhone"
              />
              <div className='field'>
                <label className='label'>Media URLs</label>
                <ul>
                  { Object.values(mediaUrls || {}).map((m, i) => (
                    <li className='field has-addons' key={i}>
                      <div className='control is-expanded'>
                        <FormField
                          autoComplete="url"
                          collectionName="events"
                          defaultValue={m}
                          entityId={id}
                          name={`mediaUrls.${i}`}
                          type="url"
                        />
                      </div>
                      <div className='control'>
                        <a className="button is-medium is-primary" onClick={e => this.deleteMediaUrl(i)}>
                          &nbsp;
                          <span className='delete'></span>
                          &nbsp;
                        </a>
                      </div>
                    </li>
                  )) }
                  <li className='has-text-right'><button className='button is-primary is-outlined is-small' onClick={this.addMediaUrl}>Ajouter une URL</button></li>
                </ul>
              </div>
              <hr />
              <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
                <div className="control">
                  <SubmitButton
                    getBody={form => form.eventsById[occasionId]}
                    getIsDisabled={form =>
                      isNew
                      ? !get(form, `eventsById.${occasionId}.description`) ||
                        !get(form, `eventsById.${occasionId}.name`) ||
                        typeof get(form, `eventsById.${occasionId}.type`) !== 'string'
                      : !get(form, `eventsById.${occasionId}.description`) &&
                        !get(form, `eventsById.${occasionId}.name`) &&
                        typeof get(form, `eventsById.${occasionId}.type`) !== 'string'
                    }
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
            </form>
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
      return Object.assign({
        collectionName: ownProps.occasionType === 'evenements'
          ? 'events'
          : ownProps.occasionType === 'things'
            ? 'things'
            : null,
        eventTypes: selectEventTypes(state),
        isNew: ownProps.occasionId === 'nouveau',
        path: selectCurrentPath(state, ownProps),
        user: state.user,
      }, selectCurrentOccasion(state, ownProps))
    },
    { resetForm, requestData }
  )
)(OfferPage)
