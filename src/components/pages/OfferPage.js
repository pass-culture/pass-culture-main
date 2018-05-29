import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import get from 'lodash.get'
import { NavLink } from 'react-router-dom'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import { requestData } from '../../reducers/data'
import selectCurrentOccasion from '../../selectors/currentOccasion'
import OccurenceManager from '../OccurenceManager'

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
      occurrences,
      website,
      mediaUrls,
    } = this.state.occasion || {}
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
              <div className='field'>
                <label className='label'>Nom</label>
                <input
                  autoComplete='name'
                  className='input title'
                  type='text'
                  name='name'
                  value={name || ''}
                  onChange={this.updateInput}
                  maxLength={140}
                />
              </div>
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
              <div className='field'>
              <label className='label'>Horaires</label>
              <OccurenceManager occurrences={occurrences} onChange={occurrences => this.updateOccasion('occurrences', occurrences)} />
              </div>
              <div className='field'>
                <label className='label'>Durée (en minutes)</label>
                <input className='input' type='number' min={0} name='durationMinutes' value={durationMinutes || ''} onChange={this.updateInput}  />
              </div>
              <div className='field'>
                <label className='label'>Date limite d'inscription (par défaut: 48h avant l'événement)</label>
                <input className='input' type='date' name='bookingLimitDatetime' value={bookingLimitDatetime || ''} onChange={this.updateInput}  />
              </div>
              <hr />
              <h2 className='subtitle is-2'>Infos artistiques</h2>
              <div className='field'>
                <label className='label'>Description</label>
                <textarea className='textarea' name='description' value={description || ''} onChange={this.updateInput} />
              </div>
              <div className='field'>
                <label className='label'>Auteur</label>
                <input className='input' type='text' name='author' value={author || ''} onChange={this.updateInput}  />
              </div>
              <div className='field'>
                <label className='label'>Metteur en scène</label>
                <input className='input' type='text' name='stageDirector' value={stageDirector || ''} onChange={this.updateInput}  />
              </div>
              <div className='field'>
                <label className='label'>Interprète</label>
                <input className='input' type='text' name='performer' value={performer || ''} onChange={this.updateInput}  />
              </div>
              <hr />
              <h2 className='subtitle is-2'>Infos de contact</h2>
              <div className='field'>
                <label className='label'>Nom du contact</label>
                <input className='input' autoComplete='name' type='text' name='contactName' value={contactName || ''} onChange={this.updateInput}  />
              </div>
              <div className='field'>
                <label className='label'>Email de contact</label>
                <input className='input' autoComplete='email' type='email' name='contactEmail' value={contactEmail || ''} onChange={this.updateInput}  />
              </div>
              <div className='field'>
                <label className='label'>Tel de contact</label>
                <input className='input' autoComplete='email' type='email' name='contactPhone' value={contactPhone || ''} onChange={this.updateInput}  />
              </div>
              <div className='field'>
                <label className='label'>Media URLs</label>
                <ul>
                  { Object.values(mediaUrls || {}).map((m, i) => (
                    <li className='field has-addons' key={i}>
                      <div className='control is-expanded'>
                        <input className='input' autoComplete='url' type='url' name={`mediaUrls.${i}`} value={m || ''} onChange={this.updateInput}  />
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
                  <button className="button is-primary is-medium">Enregistrer</button>
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
