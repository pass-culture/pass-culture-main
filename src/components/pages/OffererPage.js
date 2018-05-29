import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import get from 'lodash.get'
import { NavLink } from 'react-router-dom'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import { requestData } from '../../reducers/data'
import collectionToPath from '../../utils/collectionToPath'

class OffererPage extends Component {

  constructor() {
    super()
    this.state = {}
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    if (nextProps.isNew) return {occasion: {}}
    return {
      offerer: nextProps.offerer
    }
  }

  updateValue = e => {
    this.setState({
      offerer: Object.assign({}, this.state.offerer, {[e.target.name]: e.target.value})
    })
  }

  save = e => {
    e.preventDefault()
    // TODO
  }

  render () {
    const {
      offerer,
      isNew,
    } = this.props
    const {
      address,
      bookingEmail,
      name,
    } = get(this.state, 'offerer', {})
    const {
      latitude,
      longitude,
    } = get(this.state, 'offerer.venue', {})

    return (
      <PageWrapper name='offer' loading={!(offerer || isNew)}>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            <div className='has-text-right'>
              <NavLink to={`/${collectionToPath('venues')}`} className="button is-primary is-outlined">Retour</NavLink>
            </div>

            <h1 className='title has-text-centered'>{isNew ? 'Créer' : 'Modifier'} un lieu</h1>
            <form onSubmit={this.save}>
              <div className='field'>
                <label className='label'>Nom</label>
                <input className='input title' type='text' name='name' value={name || ''} onChange={this.updateValue} maxLength={140} />
              </div>
              <div className='field'>
                <label className='label'>Adresse</label>
                <input className='input' type='text' name='address' value={address || ''} onChange={this.updateValue}  />
              </div>
              {
                // TODO: plug this to a map
              }
              <input type='hidden' name='latitude' value={latitude || ''} />
              <input type='hidden' name='longitude' value={longitude || ''} />
              <div className='field'>
                <label className='label'>Email de réservation</label>
                <input className='input' autoComplete='email' type='email' name='bookingEmail' value={bookingEmail || ''} onChange={this.updateValue}  />
              </div>
              <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
                <div className="control">
                  <button className="button is-primary is-medium">Enregistrer</button>
                </div>
                <div className="control">
                  <NavLink to={`/${collectionToPath('venues')}`} className="button is-primary is-outlined is-medium">Retour</NavLink>
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
    (state, ownProps) => ({
      user: get(state, 'data.users.0'),
      // TODO put the following logic in a selector:
      offerer: get(state, 'user.offerers', []).find(o => o.id === get(ownProps, 'match.params.offererId', '')),
      isNew: get(ownProps, 'match.params.offererId', '') === 'nouveau',
    }),
    { requestData }
  )
)(OffererPage)
