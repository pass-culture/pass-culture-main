import React from 'react'
import { Switch, Route, Redirect } from 'react-router-dom'

import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'
import { OfferFormLayout } from 'new_components/OfferFormLayout'

import { useOfferFormSteps } from 'core/Offers'
import { fakeOffer } from 'screens/OfferIndividual/constants'
import { OfferIndividualCreationInformations as InformationsRoute } from 'routes/OfferIndividualCreationInformations'
import { OfferIndividualCreationStocks as StockRoute } from 'routes/OfferIndividualCreationStocks'
import { OfferIndividualCreationSummary as ConfirmationRoute } from 'routes/OfferIndividualCreationSummary'

const OfferIndividualCreation = (): JSX.Element => {
  const { currentStep, stepList } = useOfferFormSteps(fakeOffer)

  return (
    <OfferFormLayout>
      <OfferFormLayout.TitleBlock>
        <h1>Créer une offe</h1>
      </OfferFormLayout.TitleBlock>

      <OfferFormLayout.Stepper>
        <Breadcrumb
          activeStep={currentStep.id}
          steps={stepList}
          styleType={BreadcrumbStyle.TAB}
        />
      </OfferFormLayout.Stepper>

      <OfferFormLayout.Content>
        <Switch>
          <Route
            exact
            path={[
              '/offre/v3/creation/individuelle/informations',
              '/offre/:offerId/v3/creation/individuelle/informations',
            ]}
          >
            <InformationsRoute />
          </Route>
          <Route exact path={'/offre/:offerId/v3/creation/individuelle/stocks'}>
            <StockRoute />
          </Route>
          <Route
            exact
            path={'/offre/:offerId/v3/creation/individuelle/recapitulatif'}
          >
            <ConfirmationRoute />
          </Route>
          <Route path={''}>
            <Redirect to={'/offre/v3/creation/individuelle/informations'} />
          </Route>
        </Switch>
      </OfferFormLayout.Content>
    </OfferFormLayout>
  )
}

export default OfferIndividualCreation
