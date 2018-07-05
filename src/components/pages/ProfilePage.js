import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import get from 'lodash.get'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import UploadThumb from '../layout/UploadThumb'
import Label from '../layout/Label'
import FormField from '../layout/FormField'
import SubmitButton from '../layout/SubmitButton'
import { showNotification } from '../../reducers/notification'

import { apiUrl } from '../../utils/config'

class ProfilePage extends Component {

  handleSuccess = () => {
    const {
      showNotification
    } = this.props
    showNotification({
      type: 'success',
      text: 'Enregistré'
    })
  }

  render() {
    const {
      id,
      publicName,
      email,
      thumbPath,
    } = this.props.user || {}

    return (
      <PageWrapper name="profile" backTo={{path: '/accueil', label: 'Accueil'}}>
        <div className='section'>
          <h1 className='pc-title'>Profil</h1>
        </div>
        <div className='section'>
          <div className='field-group'>
            <FormField
              collectionName='users'
              defaultValue={publicName}
              entityId={id}
              label={<Label title="Nom :" />}
              name="publicName"
              required
              isHorizontal
            />
            <FormField
              collectionName='users'
              defaultValue={email}
              entityId={id}
              label={<Label title="Email :" />}
              name="email"
              required
              readOnly // For now there is no check on whether the email already exists so it cannot be modified
              isHorizontal
            />
          </div>
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
                handleSuccess={this.handleSuccess}
                path='users/current'
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
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    state => ({
      user: state.user,
    }), {
      showNotification,
    }
  )
)(ProfilePage)
