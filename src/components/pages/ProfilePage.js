import {
  Field,
  Form,
  showNotification,
  SubmitButton,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import PageWrapper from '../layout/PageWrapper'
import UploadThumb from '../layout/UploadThumb'
import { apiUrl } from '../../utils/config'

class ProfilePage extends Component {
  handleSuccess = () => {
    const { showNotification } = this.props
    showNotification({
      type: 'success',
      text: 'Enregistré',
    })
  }

  render() {
    const { user } = this.props
    const { id, thumbPath } = user || {}

    return (
      <PageWrapper
        name="profile"
        backTo={{ path: '/accueil', label: 'Accueil' }}
      >
        <div className="section">
          <h1 className="main-title">Profil</h1>
        </div>
        <Form
          action="users/me"
          className="section"
          handleSuccess={this.handleSuccess}
          name="editProfile"
          patch={user}
        >
          <div className="field-group">
            <Field name="publicName" label="Nom" required />
            <Field name="email" label="Email" required readOnly />
          </div>
          <div
            className="field is-grouped is-grouped-centered"
            style={{ justifyContent: 'space-between' }}
          >
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
        <h1 className="title has-text-centered">Avatar</h1>
        <div className="field">
          <UploadThumb
            className="input"
            image={apiUrl(thumbPath)}
            collectionName="users"
            storeKey="thumbedUser"
            type="thumb"
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

export default connect(
  state => ({
    user: state.user,
  }),
  {
    showNotification,
  }
)(ProfilePage)
