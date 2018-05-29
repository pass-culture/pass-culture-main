import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import get from 'lodash.get'
import { NavLink } from 'react-router-dom'
import { SingleDatePicker } from 'react-dates'

import withLogin from '../hocs/withLogin'
import Price from '../Price'
import PageWrapper from '../layout/PageWrapper'
import { requestData } from '../../reducers/data'
import selectCurrentOccasion from '../../selectors/currentOccasion'

class OfferPage extends Component {

  constructor() {
    super()
    this.state = {
      occasion: null,
      calendarFocused: false,
      time: '',
      price: 0,
      groupSize: '',
      withError: false,
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
    console.log('WTF', occasionId)
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
    this.setState({
      withError: false,
      occasion: Object.assign({}, this.state.occasion, {[key]: value})
    })
  }

  handleDateChange = date => {
    if (!this.state.time)
      return this.setState({
      withError: true
    })
    const [hours, minutes] = this.state.time.split(':')
    const datetime = date.clone().hour(hours).minute(minutes)
    const occurrences = get(this.state, 'occasion.occurrences', [])
    const isAlreadySelected = occurrences.find(o => o.datetime.isSame(datetime))
    this.updateOccasion('occurrences',
      occurrences
        .filter(o => isAlreadySelected ? !o.datetime.isSame(datetime) : true)
        .concat(isAlreadySelected ? [] : [{
          price: this.state.price,
          groupSize: this.state.groupSize,
          datetime,
        }])
        .sort((o1, o2) => o1.datetime.isBefore(o2.datetime) ? -1 : 1))
  }

  removeDate = occurrence => {
    this.updateOccasion('occurrences', get(this.state, 'occasion.occurrences', [])
      .filter(o => !o.datetime.isSame(occurrence.datetime)))
  }

  updateInput = e => {
    this.updateOccasion(e.target.name, e.target.value)
  }

  save = e => {
    e.preventDefault()
    // TODO
    const {
      collectionName,
      isNew,
      occasionId,
      requestData
    } = this.props
    const { occasion } = this.state
    e.preventDefault()
    const body = Object.assign({}, occasion)
    let path =  `occasions/${collectionName}`
    if (!isNew) {
      path = `${path}/${occasionId}`
    } else {
      // body.venueId
    }
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
      price,
      contactName,
      contactEmail,
      contactPhone,
      website,
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
                <table className='table is-striped is-hoverable'>
                  <thead>
                    <tr>
                      <td>Date</td>
                      <td>Heure</td>
                      <td>Prix</td>
                      <td>Nombre de place total</td>
                      <td>Nombre de place Personnes à Mobilité Réduite (PMR)</td>
                      <td></td>
                      <td></td>
                    </tr>
                  </thead>
                  <tbody>
                    {get(this.state, 'occasion.occurrences', []).map(o => (
                      <tr key={o.datetime} className=''>
                        <td>{o.datetime.format('DD/MM/YYYY')}</td>
                        <td>{o.datetime.format('HH:mm')}</td>
                        <td><Price value={o.price} /></td>
                        <td>{o.groupSize || 'Illimité'}</td>
                        <td>{o.pmrGroupSize || 'Illimité'}</td>
                        <td>{'?'}</td>
                        <td><button className="delete is-small" onClick={e => this.removeDate(o)}></button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <SingleDatePicker
                  calendarInfoPosition="top"
                  renderCalendarInfo={() => (
                    <div className='box content'>
                      <p className={this.state.withError ? 'has-text-weight-bold has-text-danger' : ''}>Sélectionnez d'abord l'heure, le prix et le nombre de place disponibles puis cliquez sur les dates concernées :</p>
                      <div className="field is-horizontal">
                        <div className="field-label is-normal">
                          <label className="label">Heure</label>
                        </div>
                        <div className="field-body">
                          <p>
                            <input required className='input' type='time' value={this.state.time} onChange={e => this.setState({time: e.target.value})} />
                          </p>
                        </div>
                      </div>
                      <div className="field is-horizontal">
                        <div className="field-label is-normal">
                          <label className="label">Prix</label>
                        </div>
                        <div className="field-body">
                          <p className="control has-icons-right">
                            <input className="input" type="number" placeholder="Prix" min={0} name='price' value={this.state.price} onChange={e => this.setState({price: e.target.value})} />
                            <span className="icon is-small is-right">
                              €
                            </span>
                          </p>
                        </div>
                      </div>
                      <div className="field is-horizontal">
                        <div className="field-label is-normal">
                          <label className="label">Nombre de places</label>
                        </div>
                        <div className="field-body">
                          <p className='field'>
                            <input placeholder='Laissez vide si pas de limite' className='input' type='number' min={0} name='groupSize' value={this.state.groupSize} onChange={e => this.setState({groupSize: e.target.value})}  />
                          </p>
                          <p className='field'>
                            <input placeholder='Places en PMR' className='input' type='number' min={0} name='pmrGroupSize' value={this.state.pmrGroupSize} onChange={e => this.setState({pmrGroupSize: e.target.value})}  />
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                  onDateChange={this.handleDateChange}
                  focused={this.state.calendarFocused}
                  onFocusChange={e => this.setState({calendarFocused: !this.state.calendarFocused})}
                  keepOpenOnDateSelect={true}
                  isDayHighlighted={d1 => get(this.state, 'occasion.occurrences', []).some(d2 => d1.isSame(d2.datetime, 'day'))}
                  placeholder='Ajouter un horaire'
                />
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
                <label className='label'>Site internet</label>
                <input className='input' autoComplete='url' type='url' name='website' value={website || ''} onChange={this.updateInput}  />
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
