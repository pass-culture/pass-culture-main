import React, { Component } from 'react'
import AvatarEditor from 'react-avatar-editor'
import Dropzone from 'react-dropzone'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'


import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import Icon from '../layout/Icon'
import UploadThumb from '../layout/UploadThumb'

class ProfilePage extends Component {

  constructor() {
    super()
    this.state = {
      image: null,
      zoom: 1,
    }
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    return {
      user: nextProps.user
    }
  }

  handleDrop = dropped => {
    this.setState({ image: dropped[0] })
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

    const {
      id,
      publicName,
      email,
      address,
    } = this.state.user || {}

    console.log(this.props.user)

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
                <label className='label'>Email</label>
                <input className='input' autoComplete='email' type='email' name='email' value={email || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Photo de profil</label>
                <UploadThumb
                  image={this.state.thumbUrl}
                  borderRadius={250}
                  collectionName='users'
                  entityId={id}
                  index={0}
                  width={250}
                  height={250}
                  storeKey='thumbedMediation'
                  type='thumb'
                  required
                 />
              </div>
              <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
                <div className="control">
                  <button className="button is-primary is-medium">
                    Enregistrer
                  </button>
                </div>
                <div className="control">
                  <NavLink to='/structures' className="button is-primary is-outlined is-medium">
                    Retour
                  </NavLink>
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
    state => ({
      user: state.user,
    })
  )
)(ProfilePage)
