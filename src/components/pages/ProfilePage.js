import React, { Component } from 'react'
import AvatarEditor from 'react-avatar-editor'
import Dropzone from 'react-dropzone'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import get from 'lodash.get'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import Icon from '../layout/Icon'
import UploadThumb from '../layout/UploadThumb'
import Label from '../layout/Label'
import FormField from '../layout/FormField'
import SubmitButton from '../layout/SubmitButton'

import { apiUrl } from '../../utils/config'

class ProfilePage extends Component {

  constructor() {
    super()
    this.state = {
      success: false,
      image: null,
      zoom: 1,
    }
  }

  handleDrop = dropped => {
    this.setState({ image: dropped[0] })
  }

  updateValue = e => {
    const newUser = Object.assign({}, this.state.user, {[e.target.name]: e.target.value})
    console.log(newUser)
    this.setState({
      user: newUser
    })
  }


  onSubmitClick = () => {
    this.setState({
      success: true
    })
    // const {
    //   history,
    //   resetForm,
    //   showModal
    // } = this.props
    // resetForm()
    // showModal(
    //   <div>
    //     C'est soumis!
    //   </div>,
    //   {
    //     onCloseClick: () => history.push('/offres')
    //   }
    // )
  }

  render() {

    const {
      apiPath,
    } = this.props

    const {
      id,
      publicName,
      email,
      thumbPath,
    } = this.props.user || {}
    return (
      <PageWrapper name="profile" loading={!this.props.user}>
        <h1 className='title has-text-centered'>Profil</h1>
        <div className='columns'>
          <div className='column is-half is-offset-one-quarter'>
            {this.state.success && (
              <p className='notification is-success'>
                <button class="delete" onClick={e => this.setState({success: false})}></button>
                Enregistré
              </p>
            )}
              <FormField
                collectionName='users'
                defaultValue={publicName}
                entityId={id}
                label={<Label title="Nom" />}
                name="publicName"
                className='title'
                required
              />
              <FormField
                collectionName='users'
                defaultValue={email}
                entityId={id}
                label={<Label title="Email" />}
                name="email"
                required
                readOnly // For now there is no check on whether the email already exists so it cannot be modified
              />
              <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
                <div className="control">
                  <SubmitButton
                    getBody={form => (get(form, `usersById.${id}`))}
                    getIsDisabled={form => {
                      return !get(form, `usersById.${id}.publicName`) &&
                        !get(form, `usersById.${id}.email`)
                    }}
                    className="button is-primary is-medium"
                    method='PATCH'
                    onClick={this.onSubmitClick}
                    path='users/me'
                    storeKey="occasions"
                    text="Enregistrer"
                  />
                </div>
                <div className="control">
                  <NavLink to='/accueil' className="button is-primary is-outlined is-medium">
                    Retour
                  </NavLink>
                </div>
              </div>
              <hr />
              <h1 className='title has-text-centered'>Avatar</h1>
              <div className='field'>
                <UploadThumb
                  className='input'
                  image={apiUrl(thumbPath)}
                  collectionName='users'
                  storeKey='thumbedUser'
                  type='thumb'
                  entityId={id}
                  index={0}
                  width={250}
                  height={250}
                  borderRadius={250}
                 />
              </div>
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
