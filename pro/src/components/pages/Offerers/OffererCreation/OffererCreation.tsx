import * as pcapi from 'repository/pcapi/pcapi'

import { Form } from 'react-final-form'
import GoBackLink from 'new_components/GoBackLink'
import OffererCreationForm from './OffererCreationForm/OffererCreationForm'
import OffererCreationUnavailable from './OffererCreationUnavailable/OffererCreationUnavailable'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import React from 'react'
import Titles from 'components/layout/Titles/Titles'
import { addressAndDesignationFromSirenDecorator } from 'components/layout/form/fields/SirenField'
import useActiveFeature from 'components/hooks/useActiveFeature'
import { useHistory } from 'react-router-dom'
import useNotification from 'components/hooks/useNotification'

interface iOfferer {
  id?: string
  siren?: string
}

const OffererCreation = (): JSX.Element => {
  const isEntrepriseApiDisabled = useActiveFeature('DISABLE_ENTERPRISE_API')
  const history = useHistory()
  const notification = useNotification()

  const redirectAfterSubmit = (createdOffererId: string) => {
    history.replace(`/accueil?structure=${createdOffererId}`)
  }

  const handleSubmit = async (offerer: iOfferer) => {
    const { siren } = offerer
    await pcapi
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
      <GoBackLink to="/accueil" title="Accueil" />
      <PageTitle title="Créer une structure" />
      <Titles title="Structure" />
      {isEntrepriseApiDisabled ? (
        <OffererCreationUnavailable />
      ) : (
        <Form
          backTo="/accueil"
          component={OffererCreationForm as any /* eslint-disable-line */}
          decorators={[addressAndDesignationFromSirenDecorator]}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  )
}

export default OffererCreation
