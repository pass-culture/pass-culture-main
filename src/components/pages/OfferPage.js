import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import get from 'lodash.get'
import { NavLink } from 'react-router-dom'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import { requestData } from '../../reducers/data'

class OfferPage extends Component {

  constructor() {
    super()
    this.state = {}
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    if (nextProps.isNew) return {occasion: {}}
    return {
      occasion: nextProps.occasion
    }
  }

  // handleRequestData = () => {
  //   const {
  //     match: { params: { occasionId, occasionType } },
  //     requestData
  //   } = this.props
  //   requestData('GET',
  //     `occasions/${occasionType}/${occasionId}`,
  //     { key: 'occasion' }
  //   )
  // }

  // componentDidUpdate(prevProps) {
  //   const { user } = this.props
  //   if (user && user !== prevProps.user) {
  //     this.handleRequestData()
  //   }
  // }

  updateValue = e => {
    this.setState({
      occasion: Object.assign({}, this.state.occasion, {[e.target.name]: e.target.value})
    })
  }

  render () {
    const {
      isNew,
      occasion,
      type,
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

    console.log(type)

    return (
      <PageWrapper name='offer' loading={!(occasion || isNew)}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink to='/offres' className="button is-primary is-outlined">Retour</NavLink>
            </div>
            <h1 className='title has-text-centered'>{isNew ? 'Créer' : 'Modifier'} {type === 'events' ? 'un événement' : 'un objet'}</h1>
            <form className=''>
              <div className='field'>
                <label className='label'>Nom</label>
                <input className='input title' type='text' name='name' value={name || ''} onChange={this.updateValue} maxLength={140} />
              </div>
              <div className='field'>
                <label className='label'>Type</label>
                <div className="select">
                  <select value={eventType || ''} onChange={this.updateValue}>
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
                <label className='label'>Prix</label>
                <input className='input' type='number' min={0} name='price' value={price || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Description</label>
                <textarea className='textarea' name='description' value={description || ''} onChange={this.updateValue} />
              </div>
              <div className='field'>
                <label className='label'>Auteur</label>
                <input className='input' type='text' name='author' value={author || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Metteur en scène</label>
                <input className='input' type='text' name='stageDirector' value={stageDirector || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Interprète</label>
                <input className='input' type='text' name='performer' value={performer || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Durée (en minutes)</label>
                <input className='input' type='number' min={0} name='durationMinutes' value={durationMinutes || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Places par horaire</label>
                <input className='input' type='number' min={0} name='groupSize' value={groupSize || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Places Personnes à Mobilité Réduite par horaire</label>
                <input className='input' type='number' min={0} name='pmrGroupSize' value={pmrGroupSize || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Date limite d'inscription (par défaut: 48h avant l'événement)</label>
                <input className='input' type='date' name='bookingLimitDatetime' value={bookingLimitDatetime || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Nom du contact</label>
                <input className='input' autoComplete='name' type='text' name='contactName' value={contactName || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Email de contact</label>
                <input className='input' autoComplete='email' type='email' name='contactEmail' value={contactEmail || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Tel de contact</label>
                <input className='input' autoComplete='email' type='email' name='contactPhone' value={contactPhone || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Site internet</label>
                <input className='input' autoComplete='url' type='url' name='website' value={website || ''} onChange={this.updateValue}  />
              </div>
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
  withRouter,
  connect(
    state => ({
      user: get(state, 'data.users.0'),
      // TODO put the following logic in a selector:
      occasion: get(state, 'data.occasions', []).find(o => o.id === get(state, 'router.location.pathname', '').split('/').pop()),
      isNew: get(state, 'router.location.pathname', '').split('/').pop() === 'nouveau',
      type: get(state, 'router.location.pathname', '').split('/').slice(-2)[0],
    }),
    { requestData }
  )
)(OfferPage)
