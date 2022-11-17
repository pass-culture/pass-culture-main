import cn from 'classnames'
import React, { useCallback, useEffect, useState } from 'react'
import {
  Route,
  Switch,
  useHistory,
  useLocation,
  useRouteMatch,
} from 'react-router-dom'

import { api } from 'apiClient/api'
import { LogRouteNavigation } from 'app/AppRouter/LogRouteNavigation'
import OfferBreadcrumb, {
  OfferBreadcrumbStep,
} from 'components/OfferBreadcrumb'
import useIsCompletingDraft from 'components/OfferIndividualStepper/hooks/useIsCompletingDraft'
import { RouteLeavingGuardOfferIndividualV2 } from 'components/RouteLeavingGuardOfferIndividualV2'
import {
  Events,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import Confirmation from 'pages/Offers/Offer/Confirmation/Confirmation'
import { OfferV2Summary as OfferV2SummaryRoute } from 'pages/OfferV2Summary'
import { Status } from 'screens/OfferIndividual/Status'
import { Title } from 'ui-kit'
import Titles from 'ui-kit/Titles/Titles'

import OfferDetails from './OfferDetails'
import Stocks from './Stocks/Stocks'

const mapPathToStep = {
  creation: OfferBreadcrumbStep.DETAILS,
  edition: OfferBreadcrumbStep.DETAILS,
  brouillon: OfferBreadcrumbStep.DETAILS,
  stocks: OfferBreadcrumbStep.STOCKS,
  recapitulatif: OfferBreadcrumbStep.SUMMARY,
  confirmation: OfferBreadcrumbStep.CONFIRMATION,
}

const editPageTitleByStep = {
  [OfferBreadcrumbStep.DETAILS]: 'Modifier l’offre',
  [OfferBreadcrumbStep.STOCKS]: 'Modifier l’offre',
  [OfferBreadcrumbStep.SUMMARY]: 'Récapitulatif',
}

const getActiveStepFromLocation = location => {
  let urlMatch = location.pathname.match(/[a-z]+$/)
  let stepName = urlMatch && urlMatch[0]
  // handle creation urls since the above code only works for edition urls
  if (stepName === 'individuel') {
    urlMatch = location.pathname.match(/[a-z]+\/individuel$/)
    stepName = urlMatch && urlMatch[0].split('/individuel')[0]
  }
  // handle draft completion url
  if (stepName === 'brouillon') {
    urlMatch = location.pathname.match(/\/[a-z]+\/brouillon$/)
    stepName = urlMatch && urlMatch[0].split('/individuel/')[1]
  }
  /* istanbul ignore next: DEBT, TO FIX */
  return stepName ? mapPathToStep[stepName] : null
}

const OfferLayout = () => {
  const history = useHistory()
  const location = useLocation()
  const match = useRouteMatch()
  const { logEvent } = useAnalytics()
  const isCreatingOffer = location.pathname.includes('creation')
  const isCompletingDraft = useIsCompletingDraft()
  const [offer, setOffer] = useState(null)

  const loadOffer = async offerId => {
    /* istanbul ignore next: DEBT, TO FIX */
    try {
      const existingOffer = await api.getOffer(offerId)
      setOffer(existingOffer)
    } catch {
      history.push('/404')
    }
    return Promise.resolve(null)
  }
  const activeStep = getActiveStepFromLocation(location)

  const reloadOffer = useCallback(
    /* istanbul ignore next: DEBT, TO FIX */
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

  if (match.params.offerId && !offer) {
    return null
  }

  if (isCompletingDraft) {
    pageTitle = 'Compléter l’offre'
  } else if (!isCreatingOffer) {
    /* istanbul ignore next: DEBT, TO FIX */
    if (activeStep in editPageTitleByStep) {
      pageTitle = editPageTitleByStep[activeStep]
    } else {
      pageTitle = 'Éditer l’offre'
    }
  }

  const offerHeader =
    !isCreatingOffer && !location.pathname.includes('/confirmation') ? (
      <Status
        offerId={offer.id}
        isActive={offer.isActive}
        status={offer.status}
        reloadOffer={reloadOffer}
        canDeactivate={!isCompletingDraft}
      />
    ) : null

  let offerHaveStock = false
  if (offer?.stocks !== undefined) {
    offerHaveStock = offer.stocks.length > 0
  }

  return (
    <div className="offer-page" data-testid="offer-page">
      <div
        className={cn('title-section', {
          'without-name': !offer?.name,
        })}
      >
        <Titles action={offerHeader} title={pageTitle} />
        {(!!offer?.name || activeStep !== OfferBreadcrumbStep.DETAILS) && (
          <Title as="h4" className="sub-title" level={4}>
            {offer.name}
          </Title>
        )}
      </div>
      <OfferBreadcrumb
        activeStep={activeStep}
        isCreatingOffer={isCreatingOffer}
        isCompletingDraft={isCompletingDraft}
        isOfferEducational={false}
        offerId={offer?.id}
        haveStock={offerHaveStock}
        className={
          isCreatingOffer || isCompletingDraft
            ? 'pc-breadcrumb-creation'
            : 'pc-breadcrumb-edition'
        }
      />

      <div className="offer-content">
        <Switch>
          <Route
            exact
            path={'/offre/creation/individuel'}
            render={() => (
              <LogRouteNavigation route={{ title: 'Créer une offre' }}>
                {/* FIXME (cgaunet, 2022-01-31) This is a quick win to fix a flaky E2E test */}
                {/* There is a concurrency run between the RouteLeavingGuardOfferCreation and the reloadOffer call */}
                {/* in OfferDetails as the offer is loaded in the stock edition page */}
                <OfferDetails
                  isCreatingOffer={isCreatingOffer}
                  isCompletingDraft={isCompletingDraft}
                  offer={offer}
                  reloadOffer={reloadOffer}
                />
              </LogRouteNavigation>
            )}
          />
          <Route
            exact
            path={'/offre/:offer_id/individuel/creation'}
            render={() => (
              <LogRouteNavigation route={{ title: "Éditer l'offre" }}>
                {/* FIXME (cgaunet, 2022-01-31) This is a quick win to fix a flaky E2E test */}
                {/* There is a concurrency run between the RouteLeavingGuardOfferCreation and the reloadOffer call */}
                {/* in OfferDetails as the offer is loaded in the stock edition page */}
                <OfferDetails
                  isCreatingOffer={isCreatingOffer}
                  isCompletingDraft={isCompletingDraft}
                  offer={offer}
                  reloadOffer={reloadOffer}
                />
              </LogRouteNavigation>
            )}
          />
          <Route
            exact
            path={'/offre/:offer_id/individuel/brouillon'}
            render={() => (
              <LogRouteNavigation route={{ title: "Compléter l'offre" }}>
                {/* FIXME (cgaunet, 2022-01-31) This is a quick win to fix a flaky E2E test */}
                {/* There is a concurrency run between the RouteLeavingGuardOfferCreation and the reloadOffer call */}
                {/* in OfferDetails as the offer is loaded in the stock edition page */}
                <OfferDetails
                  isCreatingOffer={isCreatingOffer}
                  isCompletingDraft={isCompletingDraft}
                  offer={offer}
                  reloadOffer={reloadOffer}
                />
              </LogRouteNavigation>
            )}
          />
          <Route
            exact
            path={`${match.path}/edition`}
            render={() => (
              <LogRouteNavigation route={{ title: "Éditer l'offre" }}>
                <OfferDetails offer={offer} reloadOffer={reloadOffer} />
              </LogRouteNavigation>
            )}
          />

          <Route
            exact
            path={`${match.path}/stocks`}
            render={() => (
              <LogRouteNavigation route={{ title: 'Éditer vos stocks' }}>
                <Stocks
                  location={location}
                  offer={offer}
                  reloadOffer={reloadOffer}
                  isCompletingDraft={isCompletingDraft}
                />
              </LogRouteNavigation>
            )}
          />
          <Route
            exact
            path={`${match.path}/creation/stocks`}
            render={() => (
              <LogRouteNavigation route={{ title: 'Créer vos stocks' }}>
                <Stocks
                  location={location}
                  offer={offer}
                  reloadOffer={reloadOffer}
                  isCompletingDraft={isCompletingDraft}
                />
              </LogRouteNavigation>
            )}
          />
          <Route
            exact
            path={`${match.path}/brouillon/stocks`}
            render={() => (
              <LogRouteNavigation route={{ title: 'Compléter vos stocks' }}>
                <Stocks
                  location={location}
                  offer={offer}
                  reloadOffer={reloadOffer}
                  isCompletingDraft={isCompletingDraft}
                />
              </LogRouteNavigation>
            )}
          />

          <Route
            exact
            path={`${match.path}/recapitulatif`}
            render={() => (
              <LogRouteNavigation
                route={{ title: 'Récapitulatif de votre offre' }}
              >
                <OfferV2SummaryRoute />
              </LogRouteNavigation>
            )}
          />

          <Route
            exact
            path={`${match.path}/creation/recapitulatif`}
            render={() => (
              <LogRouteNavigation
                route={{ title: 'Récapitulatif de votre création d’offre' }}
              >
                <OfferV2SummaryRoute />
              </LogRouteNavigation>
            )}
          />

          <Route
            exact
            path={`${match.path}/brouillon/recapitulatif`}
            render={() => (
              <LogRouteNavigation
                route={{ title: 'Récapitulatif de votre brouillon d’offre' }}
              >
                <OfferV2SummaryRoute />
              </LogRouteNavigation>
            )}
          />
          <Route
            exact
            path={`${match.path}/creation/confirmation`}
            render={() => (
              <LogRouteNavigation
                route={{
                  title: 'Confirmation de la publication de votre offre',
                }}
              >
                <Confirmation
                  offer={offer}
                  setOffer={setOffer}
                  reloadOffer={reloadOffer}
                />
              </LogRouteNavigation>
            )}
          />
          <Route
            exact
            path={`${match.path}/brouillon/confirmation`}
            render={() => (
              <LogRouteNavigation
                route={{
                  title: 'Confirmation de la publication de votre brouillon',
                }}
              >
                <Confirmation
                  offer={offer}
                  setOffer={setOffer}
                  reloadOffer={reloadOffer}
                />
              </LogRouteNavigation>
            )}
          />
        </Switch>
      </div>
      <RouteLeavingGuardOfferIndividualV2
        when={isCreatingOffer}
        tracking={nextLocation =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: activeStep,
            to: nextLocation,
            used: OFFER_FORM_NAVIGATION_OUT.ROUTE_LEAVING_GUARD,
            isEdition: !isCreatingOffer,
            isDraft: isCreatingOffer,
            offerId: offer?.id,
          })
        }
      />
    </div>
  )
}

export default OfferLayout
