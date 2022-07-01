import Breadcrumb, { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import React, { useCallback, useEffect, useState } from 'react'
import {
  Route,
  Switch,
  useHistory,
  useLocation,
  useRouteMatch,
} from 'react-router-dom'

import Confirmation from 'components/pages/Offers/Offer/Confirmation/Confirmation'
import OfferDetails from './OfferDetails'
import { OfferHeader } from 'components/pages/Offers/Offer/OfferStatus/OfferHeader'
import { OfferIndividualSummary as OfferSummaryRoute } from 'routes/OfferIndividualSummary'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import { RouteLeavingGuardOfferIndividual } from 'new_components/RouteLeavingGuardOfferIndividual'
import StocksContainer from 'components/pages/Offers/Offer/Stocks/StocksContainer'
import { Title } from 'ui-kit'
import Titles from 'components/layout/Titles/Titles'
import { api } from 'apiClient/api'
import { serializeOfferApi } from 'core/Offers/adapters/serializers'
import useActiveFeature from 'components/hooks/useActiveFeature'
import { useGetCategories } from 'core/Offers/adapters'

const mapPathToStep = {
  creation: OfferBreadcrumbStep.DETAILS,
  edition: OfferBreadcrumbStep.DETAILS,
  stocks: OfferBreadcrumbStep.STOCKS,
  recapitulatif: OfferBreadcrumbStep.SUMMARY,
  confirmation: OfferBreadcrumbStep.CONFIRMATION,
}

const getActiveStepFromLocation = location => {
  let urlMatch = location.pathname.match(/[a-z]+$/)
  let stepName = urlMatch && urlMatch[0]
  // handle creation urls since the above code only works for edition urls
  if (stepName === 'individuel') {
    urlMatch = location.pathname.match(/[a-z]+\/individuel$/)
    stepName = urlMatch && urlMatch[0].split('/individuel')[0]
  }

  return stepName ? mapPathToStep[stepName] : null
}

const OfferLayout = () => {
  const history = useHistory()
  const location = useLocation()
  const match = useRouteMatch()
  const isCreatingOffer = location.pathname.includes('creation')
  const [offer, setOffer] = useState(null)
  const useSummaryPage = useActiveFeature('OFFER_FORM_SUMMARY_PAGE')

  const { data: categoriesData, isLoading: isLoadingCategories } =
    useGetCategories()
  const loadOffer = async offerId => {
    try {
      const existingOffer = await api.getOffer(offerId)
      setOffer(existingOffer)
    } catch {
      history.push('/404')
    }
  }
  const activeStep = getActiveStepFromLocation(location)

  const reloadOffer = useCallback(
    async () => (offer.id ? await loadOffer(offer.id) : false),
    [offer?.id]
  )

  useEffect(() => {
    async function loadOfferFromQueryParam() {
      await loadOffer(match.params.offerId)
    }
    match.params.offerId && loadOfferFromQueryParam()
  }, [match.params.offerId])

  let pageTitle = 'Créer une offre'

  if (isLoadingCategories || (match.params.offerId && !offer)) {
    return null
  }

  if (!isCreatingOffer) {
    pageTitle = 'Éditer une offre'
  }

  const offerHeader =
    !isCreatingOffer && !location.pathname.includes('/confirmation') ? (
      <OfferHeader offer={offer} reloadOffer={reloadOffer} />
    ) : null

  if (offer?.isEducational) {
    history.push(
      `/offre/${match.params.offerId}/collectif/${
        activeStep === 'stocks' ? 'stocks/edition' : 'edition'
      }`
    )
  }

  let offerHaveStock = false
  if (offer?.stocks !== undefined) {
    offerHaveStock = offer.stocks.length > 0
  }

  return (
    <div className="offer-page">
      <div className="title-section">
        <Titles action={offerHeader} title={pageTitle} />
        {(!isCreatingOffer || activeStep !== OfferBreadcrumbStep.DETAILS) && (
          <Title as="h4" className="sub-title" level={4}>
            {offer.name}
          </Title>
        )}
      </div>

      <Breadcrumb
        activeStep={activeStep}
        isCreatingOffer={isCreatingOffer}
        isOfferEducational={offer?.isEducational}
        offerId={offer?.id}
        haveStock={offerHaveStock}
      />

      <div className="offer-content">
        <Switch>
          <Route
            exact
            path={[
              '/offre/creation/individuel',
              '/offre/:offer_id/individuel/creation',
            ]}
          >
            {/* FIXME (cgaunet, 2022-01-31) This is a quick win to fix a flaky E2E test */}
            {/* There is a concurrency run between the RouteLeavingGuardOfferCreation and the reloadOffer call */}
            {/* in OfferDetails as the offer is loaded in the stock edition page */}
            <OfferDetails
              isCreatingOffer={isCreatingOffer}
              offer={offer}
              reloadOffer={reloadOffer}
            />
          </Route>
          <Route exact path={`${match.url}/edition`}>
            <OfferDetails offer={offer} reloadOffer={reloadOffer} />
          </Route>
          <Route
            exact
            path={[`${match.url}/stocks`, `${match.url}/creation/stocks`]}
          >
            <StocksContainer
              location={location}
              offer={offer}
              reloadOffer={reloadOffer}
            />
          </Route>
          <Route
            exact
            path={[
              `${match.path}/recapitulatif`,
              `${match.path}/creation/recapitulatif`,
            ]}
          >
            {() => (
              <OfferSummaryRoute
                formOfferV2={true}
                offerId={offer.id}
                offer={serializeOfferApi(offer)}
                categories={categoriesData.categories}
                subCategories={categoriesData.subCategories}
              />
            )}
          </Route>
          <Route exact path={`${match.url}/creation/confirmation`}>
            {() => <Confirmation offer={offer} setOffer={setOffer} />}
          </Route>
        </Switch>
      </div>
      {useSummaryPage ? (
        <RouteLeavingGuardOfferIndividual when={isCreatingOffer} />
      ) : (
        <RouteLeavingGuardOfferCreation when={isCreatingOffer} />
      )}
    </div>
  )
}

export default OfferLayout
