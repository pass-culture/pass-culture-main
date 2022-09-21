import React from 'react'
import { Form } from 'react-final-form'
import { useHistory } from 'react-router-dom'

import { api } from 'apiClient/api'
import { CreateOffererQueryModel } from 'apiClient/v1'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'
import { addressAndDesignationFromSirenDecorator } from 'components/layout/form/fields/SirenField'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import GoBackLink from 'new_components/GoBackLink'

import OffererCreationForm from './OffererCreationForm/OffererCreationForm'
import OffererCreationUnavailable from './OffererCreationUnavailable/OffererCreationUnavailable'

const OffererCreation = (): JSX.Element => {
  const isEntrepriseApiDisabled = useActiveFeature('DISABLE_ENTERPRISE_API')
  const history = useHistory()
  const notification = useNotification()

  const redirectAfterSubmit = (createdOffererId: string) => {
    history.replace(`/accueil?structure=${createdOffererId}`)
  }

  const handleSubmit = async (offerer: CreateOffererQueryModel) => {
    const { siren } = offerer

    await api
      .createOfferer({
        ...offerer,
        siren: siren?.replace(/\s/g, ''),
      })
      .then(offerer => {
        onHandleSuccess(offerer.id)
      })
      .catch(() => {
        onHandleFail()
      })
  }

  const onHandleSuccess = (offererId: string) => {
    redirectAfterSubmit(offererId)
  }

  const onHandleFail = () => {
    notification.error('Vous étes déjà rattaché à cette structure.')
  }

  return (
    <div className="offerer-page">
      <GoBackLink
        to="/accueil"
        title="Accueil"
        className="offerer-page-go-back-link"
      />
      <PageTitle title="Créer une structure" />
      <Titles title="Structure" />
      {isEntrepriseApiDisabled ? (
        <OffererCreationUnavailable />
      ) : (
        <Form<CreateOffererQueryModel>
          component={({ handleSubmit, invalid, pristine }) => (
            <OffererCreationForm
              backTo="/accueil"
              handleSubmit={handleSubmit}
              invalid={invalid}
              pristine={pristine}
            />
          )}
          decorators={[addressAndDesignationFromSirenDecorator]}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  )
}

export default OffererCreation
