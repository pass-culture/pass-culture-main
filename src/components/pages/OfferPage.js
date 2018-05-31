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
import { NEW } from '../../utils/config'
import { collectionToPath, pathToCollection} from '../../utils/translate'

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

    const occasionIdOrNew = isNew ? NEW : occasionId
    const occasionCollectionName = pathToCollection(occasionPath)
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
            <form>
              <FormField
                autoComplete="name"
                collectionName={occasionCollectionName}
                defaultValue={name}
                entityId={occasionId}
                label={<Label title="Titre" />}
                name="name"
              />
              <hr />
              <h2 className='subtitle is-2'>Infos pratiques</h2>
              <FormField
                collectionName={occasionCollectionName}
                defaultValue={type || ''}
                entityId={occasionId}
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
                collectionName={occasionCollectionName}
                defaultValue={durationMinutes}
                entityId={occasionId}
                label={<Label title="Durée (en minutes)" />}
                name="durationMinutes"
                type="number"
              />
              <FormField
                autoComplete="bookingLimitDatetimes"
                collectionName={occasionCollectionName}
                defaultValue={bookingLimitDatetime}
                entityId={occasionId}
                label={<Label title="Date limite d'inscription (par défaut: 48h avant l'événement)" />}
                name="bookingLimitDatetime"
                type="date"
              />

              <hr />
              <h2 className='subtitle is-2'>Infos artistiques</h2>
              <FormField
                autoComplete="description"
                collectionName={occasionCollectionName}
                defaultValue={description}
                entityId={occasionId}
                label={<Label title="Description" />}
                name="description"
                type="textarea"
              />
              <FormField
                autoComplete="author"
                collectionName={occasionCollectionName}
                defaultValue={author}
                entityId={occasionId}
                label={<Label title="Auteur" />}
                name="author"
              />
              <FormField
                autoComplete="stageDirector"
                collectionName={occasionCollectionName}
                defaultValue={stageDirector}
                entityId={occasionId}
                label={<Label title="Metteur en scène" />}
                name="stageDirector"
              />
              <FormField
                autoComplete="performer"
                collectionName={occasionCollectionName}
                defaultValue={performer}
                entityId={occasionId}
                label={<Label title="Interprète" />}
                name="performer"
              />
              <hr />
              <h2 className='subtitle is-2'>Infos de contact</h2>
              <FormField
                autoComplete="contactName"
                collectionName={occasionCollectionName}
                defaultValue={contactName}
                entityId={occasionId}
                label={<Label title="Nom du contact" />}
                name="contactName"
              />
              <FormField
                autoComplete="contactEmail"
                collectionName={occasionCollectionName}
                defaultValue={contactEmail}
                entityId={occasionId}
                label={<Label title="Email de contact" />}
                name="contactEmail"
                type="email"

              />
              <FormField
                autoComplete="contactPhone"
                collectionName={occasionCollectionName}
                defaultValue={contactPhone}
                entityId={occasionId}
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
                          collectionName={occasionCollectionName}
                          defaultValue={m}
                          entityId={occasionId}
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
                    getBody={form => form.eventsById[occasionIdOrNew]}
                    getIsDisabled={form =>
                      isNew
                      ? !get(form, `eventsById.${occasionIdOrNew}.description`) ||
                        !get(form, `eventsById.${occasionIdOrNew}.name`) ||
                        typeof get(form, `eventsById.${occasionIdOrNew}.type`) !== 'string'
                      : !get(form, `eventsById.${occasionIdOrNew}.description`) &&
                        !get(form, `eventsById.${occasionIdOrNew}.name`) &&
                        typeof get(form, `eventsById.${occasionIdOrNew}.type`) !== 'string'
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
      return {
        user: state.user,
        occasionPath: ownProps.match.params.occasionPath,
        occasionId: ownProps.match.params.occasionId,
        isNew: ownProps.match.params.occasionId === 'nouveau',
        eventTypes: selectEventTypes(state),
        path: selectCurrentPath(state, ownProps),
        occasion: selectCurrentOccasion(state, ownProps),
      }
    },
    { resetForm, requestData }
  )
)(OfferPage)
