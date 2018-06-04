import React, { Component } from 'react'
import AvatarEditor from 'react-avatar-editor'
import Dropzone from 'react-dropzone'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'


import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import Icon from '../layout/Icon'

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
                <label className='label'>Email</label>
                <input className='input' autoComplete='email' type='email' name='email' value={email || ''} onChange={this.updateValue}  />
              </div>
              <div className='field'>
                <label className='label'>Photo de profil</label>
                <Dropzone
                  className={`input profile-pic ${this.state.image && 'has-image'}`}
                  onDrop={this.handleDrop}
                  disableClick={Boolean(this.state.image)}
                >
                  {
                    this.state.image
                    ? (
                      <button
                        onClick={ e => this.setState({image: null})}
                        className='remove-image'>
                        <Icon svg='ico-close-b' alt="Enlever l'image" />
                      </button>
                    )
                    : (
                      <p className="drag-n-drop">
                        Cliquez ou glissez-déposez pour charger une image
                      </p>
                    )
                  }
                  <AvatarEditor
                    width={250}
                    height={250}
                    scale={this.state.zoom}
                    border={50}
                    borderRadius={250}
                    color={[255, 255, 255, this.state.image ? 0.6 : 1]}
                    image={this.state.image}
                  />
                  {
                    this.state.image && (
                      <input
                        className="zoom"
                        type="range"
                        min="1"
                        max="2"
                        step="0.01"
                        value={this.state.zoom}
                        onChange={e => this.setState({zoom: parseFloat(e.target.value)})}
                      />
                    )
                  }
                </Dropzone>
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
