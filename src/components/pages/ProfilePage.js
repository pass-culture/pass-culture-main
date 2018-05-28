import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import get from 'lodash.get'
import { NavLink } from 'react-router-dom'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import { requestData } from '../../reducers/data'

class ProfilePage extends Component {

  constructor() {
    super()
    this.state = {}
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    return {
      user: nextProps.user
    }
  }

  updateValue = e => {
    this.setState({
      user: Object.assign({}, this.state.occasion, {[e.target.name]: e.target.value})
    })
  }

  save = e => {
    // TODO
  }

  render() {

    console.log(this.props.user)

    const {
      publicName,
      email,
      address,

    } = this.state.user || {}

    return (
      <PageWrapper name="profile" loading={!this.props.user}>
        <h1 className='title has-text-centered'>Profil</h1>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>

            <form onSubmit={this.save}>
              <div className='field'>
                <label className='label'>Nom</label>
                <input className='input title' type='text' name='publicName' value={publicName || ''} onChange={this.updateValue} maxLength={140} />
              </div>
              <div className='field'>
                <label className='label'>Adresse</label>
                <input className='input' type='text' name='address' value={address || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Email de réservation</label>
                <input className='input' autoComplete='email' type='email' name='email' value={email || ''} onChange={this.updateValue}  />
              </div>
              <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
                <div className="control">
                  <button className="button is-primary is-medium">Enregistrer</button>
                </div>
                <div className="control">
                  <NavLink to='/lieux' className="button is-primary is-outlined is-medium">Retour</NavLink>
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
      user: get(state, 'user'),
    }),
    { requestData }
  )
)(ProfilePage)
