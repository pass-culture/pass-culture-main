import get from 'lodash.get'
import { Field, Form, SubmitButton, withLogin } from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import HeroSection from '../layout/HeroSection'
import Main from '../layout/Main'
import UploadThumb from '../layout/UploadThumb'
import { apiUrl } from '../../utils/config'

const backTo = { path: '/accueil', label: 'Accueil' }

const ProfilePage = ({ user }) => {
  const userId = get(user, 'id')
  const thumbPath = get(user, 'thumbPath')

  return (
    <Main name="profile" backTo={backTo}>
      <HeroSection title="Profil" />
      <Form
        action="/users/current"
        className="section"
        name="editProfile"
        patch={user || {}}>
        <div className="field-group">
          <Field name="publicName" label="Nom" required />
          <Field name="email" label="Email" required readOnly />
        </div>
        <div
          className="field is-grouped is-grouped-centered"
          style={{ justifyContent: 'space-between' }}>
          <div className="control">
            <SubmitButton className="button is-primary is-medium">
              Enregistrer
            </SubmitButton>
          </div>
          <div className="field">
            <Field name="email" type="email" label="Email" required />
          </div>
        </div>
      </Form>
      <hr />
      {false && <h1 className="title has-text-centered">Avatar</h1>}
      {false && (
        <div className="field">
          <UploadThumb
            className="input"
            image={apiUrl(thumbPath)}
            collectionName="users"
            storeKey="thumbedUser"
            type="thumb"
            entityId={userId}
            index={0}
            width={250}
            height={250}
            borderRadius={250}
          />
        </div>
      )}
    </Main>
  )
}

function mapStateToProps(state) {
  return {
    user: state.user,
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  connect(mapStateToProps)
)(ProfilePage)
