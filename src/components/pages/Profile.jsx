import { Field, Form, SubmitButton } from 'pass-culture-shared'
import React from 'react'
import { compose } from 'redux'

import { withRedirectToSigninWhenNotAuthenticated } from '../hocs'
import HeroSection from '../layout/HeroSection'
import Main from '../layout/Main'
import UploadThumb from '../layout/UploadThumb'
import { apiUrl } from '../../utils/config'

const backTo = { path: '/accueil', label: 'Accueil' }

const ProfilePage = ({ currentUser }) => {
  const { thumbPath, userId } = currentUser || {}

  return (
    <Main name="profile" backTo={backTo}>
      <HeroSection title="Profil" />
      <Form
        action="/users/current"
        className="section"
        name="editProfile"
        patch={currentUser}>
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

export default compose(withRedirectToSigninWhenNotAuthenticated)(ProfilePage)
