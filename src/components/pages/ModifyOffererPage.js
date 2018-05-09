import React from 'react'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import FormField from '../layout/FormField'
import PageWrapper from '../layout/PageWrapper'

const Label = ({ title }) => (
  <div>
    <h3 className='subtitle'>{title}</h3>
  </div>
)

const ModifyOffererPage = ({ match: { params: { offererId } } }) => {
  return (
    <PageWrapper name='modify-offerer' noPadding>
      <section class="hero">
        <div class="hero-body">
          <div class="container">
            <h1 class="title">
              {
                offererId === 'creation'
                  ? 'Créez votre espace'
                  : 'Modifiez votre espace'
              }
            </h1>
          </div>
        </div>
      </section>

      <div className="box form-container">
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
          name="adress"
          autoComplete="adress"
          placeholder="8, boulevard des Capucines"
          type="text"
        />
      </div>

      <section class="hero">
        <div class="hero-body">
          <div class="container">
            <h1 class="title">
              Définir une image
            </h1>
          </div>
        </div>
      </section>
    </PageWrapper>
  )
}

export default compose(
  withLogin({ isRequired: true }),
  withRouter
)(ModifyOffererPage)
