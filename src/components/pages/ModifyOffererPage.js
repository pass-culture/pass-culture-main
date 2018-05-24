import React from 'react'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import SubmitButton from '../layout/SubmitButton'
import PageWrapper from '../layout/PageWrapper'

const Label = ({ title }) => (
  <div>
    <h3 className='subtitle'>{title}</h3>
  </div>
)

const ModifyOffererPage = ({ match: { params: { offererId } } }) => {
  return (
    <PageWrapper name='modify-offerer' noPadding>
      <section className="hero">
        <div className="hero-body">
          <div className="container">
            <h1 className="title has-text-centered">
              {
                offererId === 'creation'
                  ? 'Créez votre espace'
                  : 'Modifiez votre espace'
              }
            </h1>
          </div>
        </div>
      </section>

      <form className="box form-container">
        <FormField
          label={
            <Label
              title="Nom"
            />
          }
          required="true"
          collectionName="offerer"
          name="name"
          autoComplete="name"
          placeholder=""
          type="text"
        />

        {
          /*TODO: FIND GEOLOCATION*/
        }
        <FormField
          label={
            <Label
              title="Adresse"
            />
          }
          required="true"
          collectionName="venues"
          name="address"
          autoComplete="address"
          placeholder="3 rue de Valois, 75001 Paris"
          type="text"
        />
        <FormField
          label={
            <Label
              title="Email"
            />
          }
          required="true"
          collectionName="venues"
          name="email"
          autoComplete="email"
          placeholder="nom@exemple.com"
          type="email"
        />
        <FormField
          label={
            <Label
              title="Image"
            />
          }
          required="true"
          collectionName="venues"
          name="image"
          type="file"
        />
        <SubmitButton className='button is-primary' path='/' />
      </form>
    </PageWrapper>
  )
}

export default compose(
  withLogin({ isRequired: true }),
  withRouter
)(ModifyOffererPage)
