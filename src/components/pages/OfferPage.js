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
import selectCurrentOccasion from '../../selectors/currentOccasion'
import { NEW } from '../../utils/config'

const Label = ({ title }) => {
  return <div className="title">{title}</div>
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

  updateInput = e => {
    this.updateOccasion(e.target.name, e.target.value)
  }

  addMediaUrl = () => {
    this.updateOccasion('mediaUrls', Object.values(get(this.state, 'occasion.mediaUrls', [])).concat(''))
  }

  deleteMediaUrl = index => {
    this.updateOccasion('mediaUrls', Object.values(get(this.state, 'occasion.mediaUrls', [])).filter((_, i) => index !== i))
  }

  save = e => {
    // prevent to do a page refresh
    e.preventDefault()

    // TODO
    const {
      collectionName,
      isNew,
      occasionId,
      requestData
    } = this.props
    const { occasion } = this.state

    // NOTE: for now we don't do field type validation
    // so we provide default values just for making the api working
    const body = Object.assign(
      isNew
        ? {
          description: '',
          durationMinutes: '0h30',
          name: ''
        }
        : {},
      occasion
    )

    let path =  `occasions/${collectionName}`
    if (!isNew) {
      path = `${path}/${occasionId}`
    } else {
      // body.venueId
    }




    console.log('body', body)
    requestData(
      isNew
        ? 'POST'
        : 'PATCH',
      path,
      {
        body,
        key: 'occasion'
      }
    )
  }

  render () {
    const {
      isNew,
      occasion,
      occasionType,
    } = this.props
    const {
      author,
      stageDirector,
      performer,
      name,
      description,
      durationMinutes,
      eventType,
      groupSize,
      pmrGroupSize,
      bookingLimitDatetime,
      contactName,
      contactEmail,
      contactPhone,
      website,
      mediaUrls,
    } = this.state.occasion || {}
    const occurences = (this.state.occasion && this.state.occasion.occurences)
      || (occasion && occasion.occurences)
    const occasionId = isNew ? NEW : this.props.occasionId
    return (
      <PageWrapper name='offer' loading={!(occasion || isNew)}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink to='/offres' className="button is-primary is-outlined">
                Retour
              </NavLink>
            </div>
            <h1 className='title has-text-centered'>
              {isNew ? 'Créer' : 'Modifier'} {occasionType === 'events' ? 'un événement' : 'un objet'}
            </h1>
            <form onSubmit={this.save}>
              <FormField
                defaultValue={name}
                collectionName="events"
                label={<Label title="Titre" />}
                name="name"
                placeholder=""
                autoComplete="name"
              />
              <hr />
              <h2 className='subtitle is-2'>Infos pratiques</h2>
              <div className='field'>
                <label className='label'>Type</label>
                <div className="select">
                  <select value={eventType || ''} onChange={this.updateInput}>
                    <option>Atelier</option>
                    <option>Exposition</option>
                    <option>Spectacle</option>
                    <option>Théâtre</option>
                    <option>Concert</option>
                    <option>Danse</option>
                    <option>Festival</option>
                    <option>Musée</option>
                    <option>Documentaire</option>
                  </select>
                </div>
              </div>
              -
              <div className='field'>
                <label className='label'>Horaires</label>
                <OccurenceManager occurences={occurences} onChange={occurences => this.updateOccasion('occurences', occurences)} />
              </div>

              <FormField
                defaultValue={durationMinutes}
                type="number"
                collectionName="events"
                label={<Label title="Durée (en minutes)" />}
                name="durationMinutes"
                placeholder=""
                autoComplete="durationMinutes"
              />
              <FormField
                defaultValue={bookingLimitDatetime}
                type="date"
                collectionName="events"
                label={<Label title="Date limite d'inscription (par défaut: 48h avant l'événement)" />}
                name="bookingLimitDatetime"
                placeholder=""
                autoComplete="durationMinutes"
              />

              <hr />
              <h2 className='subtitle is-2'>Infos artistiques</h2>
              <FormField
                defaultValue={description}
                type="textarea"
                collectionName="events"
                label={<Label title="Description" />}
                name="description"
                placeholder=""
                autoComplete="description"
              />
              <FormField
                defaultValue={bookingLimitDatetime}
                type="date"
                collectionName="events"
                label={<Label title="Date limite d'inscription (par défaut: 48h avant l'événement)" />}
                name="bookingLimitDatetime"
                placeholder=""
                autoComplete="durationMinutes"
              />
              <FormField
                defaultValue={author}
                collectionName="events"
                label={<Label title="Auteur" />}
                name="author"
                placeholder=""
                autoComplete="author"
              />
              <FormField
                defaultValue={stageDirector}
                collectionName="events"
                label={<Label title="Metteur en scène" />}
                name="stageDirector"
                placeholder=""
                autoComplete="stageDirector"
              />
              <FormField
                defaultValue={performer}
                collectionName="events"
                label={<Label title="Interprète" />}
                name="performer"
                placeholder=""
                autoComplete="performer"
              />
              <hr />
              <h2 className='subtitle is-2'>Infos de contact</h2>
              <FormField
                defaultValue={contactName}
                collectionName="events"
                label={<Label title="Nom du contact" />}
                name="contactName"
                placeholder=""
                autoComplete="contactName"
              />
              <FormField
                defaultValue={contactEmail}
                collectionName="events"
                label={<Label title="Email de contact" />}
                name="contactEmail"
                placeholder=""
                type="email"
                autoComplete="contactEmail"
              />
              <FormField
                defaultValue={contactPhone}
                collectionName="events"
                label={<Label title="Tel de contact" />}
                name="contactPhone"
                placeholder=""
                autoComplete="contactPhone"
              />
              <div className='field'>
                <label className='label'>Media URLs</label>
                <ul>
                  { Object.values(mediaUrls || {}).map((m, i) => (
                    <li className='field has-addons' key={i}>
                      <div className='control is-expanded'>
                        <FormField
                          defaultValue={m}
                          collectionName="events"
                          name={`mediaUrls.${i}`}
                          placeholder=""
                          type="url"
                          autoComplete="url"
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
                      !get(form, `eventsById.${occasionId}.description`) ||
                      !get(form, `eventsById.${occasionId}.name`)
                    }
                    className="button is-primary is-medium"
                    path={`occasions/${occasionType}`}
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
        collectionName: ownProps.occasionType === 'evenements'
          ? 'events'
          : ownProps.occasionType === 'things'
            ? 'things'
            : null,
        user: state.user,
        occasion: selectCurrentOccasion(state, ownProps),
        isNew: ownProps.occasionId === 'nouveau',
      }
    },
    { requestData }
  )
)(OfferPage)
