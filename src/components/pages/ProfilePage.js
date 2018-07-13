import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import UploadThumb from '../layout/UploadThumb'
import { showNotification } from '../../reducers/notification'

import { apiUrl } from '../../utils/config'

import Form from '../layout/Form'
import Field from '../layout/Field'
import Submit from '../layout/Submit'

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
      thumbPath,
    } = this.props.user || {}

    return (
      <PageWrapper name="profile" backTo={{path: '/accueil', label: 'Accueil'}}>
        <div className='section'>
          <h1 className='pc-title'>Profil</h1>
        </div>
        <Form className='section' name='editProfile' action='users/me' data={this.props.user} handleSuccess={this.handleSuccess}>
          <div className='field-group'>
            <Field name='publicName' label='Nom' required />
            <Field name='email' label='Email' required readOnly />
          </div>
          <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
            <div className="control">
              <Submit className='button is-primary is-medium'>Enregistrer</Submit>
            </div>
            <div className="control">
              <NavLink to='/accueil' className="button is-primary is-outlined is-medium">
                Retour
              </NavLink>
            </div>
          </div>
        </Form>
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
