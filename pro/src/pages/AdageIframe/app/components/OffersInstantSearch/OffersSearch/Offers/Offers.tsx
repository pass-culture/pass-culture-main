import { useEffect } from 'react'
import {
  useInfiniteHits,
  useInstantSearch,
  usePagination,
  useStats,
} from 'react-instantsearch'
import { useLocation } from 'react-router'
import useSWR from 'swr'

import {
  AdageFrontRoles,
  type CollectiveOfferResponseModel,
  type CollectiveOfferTemplateResponseModel,
  type VenueResponse,
} from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { GET_COLLECTIVE_OFFER_TEMPLATES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useAccessibleScroll } from '@/commons/hooks/useAccessibleScroll'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { setSearchView } from '@/commons/store/adageFilter/reducer'
import { adageSearchViewSelector } from '@/commons/store/adageFilter/selectors'
import { LOGS_DATA } from '@/commons/utils/config'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { AccessibleScrollContainer } from '@/components/AccessibleScrollContainer/AccessibleScrollContainer'
import {
  HighlightBanner,
  HighlightBannerVariant,
} from '@/components/HighlightBanner/HighlightBanner'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullGoTopIcon from '@/icons/full-go-top.svg'
import fullGridIcon from '@/icons/full-grid.svg'
import fullLinkIcon from '@/icons/full-link.svg'
import fullListIcon from '@/icons/full-list.svg'
import { useAdageUser } from '@/pages/AdageIframe/app/hooks/useAdageUser'
import { isCollectiveOfferTemplate } from '@/pages/AdageIframe/app/types'
import { ShadowTipsHelpIcon } from '@/ui-kit/Icons/SVGs/ShadowTipsHelpIcon'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { OfferCardComponent } from '../../../AdageDiscovery/OfferCard/OfferCard'
import { CustomPagination } from '../../../Pagination/Pagination'
import { AdageSkeleton } from '../../../Skeleton/AdageSkeleton'
import { SurveySatisfaction } from '../../../SurveySatisfaction/SurveySatisfaction'
import {
  type ToggleButton,
  ToggleButtonGroup,
} from '../../../ToggleButtonGroup/ToggleButtonGroup'
import { AdageOfferListCard } from './AdageOfferListCard/AdageOfferListCard'
import TFD2025 from './assets/TFD2025.svg'
import { NoResultsPage } from './NoResultsPage/NoResultsPage'
import styles from './Offers.module.scss'

export interface OffersProps {
  displayStats?: boolean
  displayShowMore?: boolean
  displayNoResult?: boolean
  submitCount?: number
  isBackToTopVisibile?: boolean
  indexId?: string //  IndexId is necessary if the component is within the scope of a react-instantsearch <Index />
  venue?: VenueResponse | null
}

export const Offers = ({
  displayStats = true,
  displayNoResult = true,
  submitCount,
  isBackToTopVisibile = false,
  indexId,
  venue,
}: OffersProps): JSX.Element | null => {
  const dispatch = useAppDispatch()

  const adageViewType = useAppSelector(adageSearchViewSelector)
  const { currentPageHits: hits } = useInfiniteHits()
  const { nbHits } = useStats()
  const { scopedResults, results: nonScopedResult } = useInstantSearch()

  const isMobileScreen = useMediaQuery('(max-width: 64rem)')

  const location = useLocation()

  const results = indexId
    ? scopedResults.find((res) => res.indexId === indexId)?.results
    : nonScopedResult

  const highlightTargetDate = new Date('2025-08-10').getTime()
  const currentDate = Date.now()

  const showDiffuseHelp =
    (submitCount ?? 0) > 0 && currentDate >= highlightTargetDate

  const isInSuggestions = indexId?.startsWith('no_results_offers')

  const { adageUser } = useAdageUser()

  const showSurveySatisfaction =
    !adageUser.preferences?.feedback_form_closed &&
    adageUser.role !== AdageFrontRoles.READONLY

  const hitsIds = hits.map((hit) => Number(hit.objectID.replace('T-', '')))
  const { data, isLoading } = useSWR(
    hitsIds.length > 0
      ? [GET_COLLECTIVE_OFFER_TEMPLATES_QUERY_KEY, ...hitsIds]
      : null,
    ([, ...offererIdParam]) =>
      apiAdage.getCollectiveOfferTemplates(offererIdParam)
  )

  const fetchedOffers = data?.collectiveOffers ?? []

  //  Reorder the fetched offers in the order of the initial algolia hits
  const offers = hits
    .map((hit) =>
      fetchedOffers.find((offerTmp) => `T-${offerTmp.id}` === hit.objectID)
    )
    .filter((offer) => !!offer)

  useEffect(() => {
    if (isMobileScreen !== undefined) {
      apiAdage.logOfferListViewSwitch({
        iframeFrom: location.pathname,
        source: adageViewType,
        isMobile: isMobileScreen,
      })
    }
  }, [isMobileScreen])

  useEffect(() => {
    if (isMobileScreen) {
      dispatch(setSearchView('grid'))
    }
  }, [isMobileScreen, dispatch])

  const { currentRefinement, nbPages } = usePagination()
  const { contentWrapperRef, scrollToContentWrapper } = useAccessibleScroll()

  if (isLoading && offers.length === 0) {
    return (
      <div className={styles['offers-loader']}>
        <AdageSkeleton />
        <AdageSkeleton />
        <AdageSkeleton />
      </div>
    )
  }

  if (hits.length === 0 || offers.length === 0 || !results) {
    return displayNoResult ? (
      <NoResultsPage query={results?.query} venue={venue} />
    ) : null
  }

  function toggleButtonClicked(button: ToggleButton) {
    const viewType = button.id === 'list' ? 'list' : 'grid'
    const source = button.id === 'list' ? 'grid' : 'list'
    dispatch(setSearchView(viewType))
    if (adageViewType !== viewType) {
      apiAdage.logOfferListViewSwitch({
        iframeFrom: location.pathname,
        source,
        isMobile: isMobileScreen,
      })
    }
  }

  function triggerOfferClickLog(
    offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  ) {
    if (!LOGS_DATA) {
      return
    }

    apiAdage.logOfferTemplateDetailsButtonClick({
      iframeFrom: location.pathname,
      offerId: isCollectiveOfferTemplate(offer) ? offer.id : offer.stock.id,
      queryId: results?.queryID,
      isFromNoResult: isInSuggestions,
      vueType: adageViewType,
    })
  }

  const logOpenHighlightBanner = (bannerName: string) => {
    apiAdage.logOpenHighlightBanner({
      iframeFrom: location.pathname,
      queryId: results.queryID,
      banner: bannerName,
    })
  }

  return (
    <>
      {!isInSuggestions && (
        <ToggleButtonGroup
          className={styles['offer-type-vue']}
          groupLabel="Choix du type de vue des offres"
          buttons={[
            {
              label: 'Vue liste',
              id: 'list',
              content: <SvgIcon width="24" src={fullListIcon} alt="" />,
              onClick: toggleButtonClicked,
            },
            {
              label: 'Vue grille',
              id: 'grid',
              content: <SvgIcon width="24" src={fullGridIcon} alt="" />,
              onClick: toggleButtonClicked,
            },
          ]}
          activeButton={adageViewType}
        />
      )}
      <div className={styles['offers-view']}>
        {displayStats && (
          <div className={styles['offers-stats']}>
            {new Intl.NumberFormat('fr-FR').format(nbHits)}{' '}
            {pluralizeFr(nbHits, 'offre', 'offres')} au total
          </div>
        )}
      </div>
      <AccessibleScrollContainer
        containerRef={contentWrapperRef}
        liveMessage={`Page ${currentRefinement + 1} sur ${nbPages}`}
      >
        <ul
          className={
            styles[`offers-${isInSuggestions ? 'list' : adageViewType}`]
          }
        >
          {offers.map((offer, index) => (
            <li
              key={`${offer.isTemplate ? 'T' : ''}${offer.id}`}
              data-testid="offer-listitem"
            >
              {adageViewType === 'list' || isInSuggestions ? (
                <AdageOfferListCard
                  offer={offer}
                  queryId={results.queryID ?? ''}
                  isInSuggestions={indexId?.startsWith('no_results_offers')}
                  viewType={adageViewType}
                  onCardClicked={() => triggerOfferClickLog(offer)}
                />
              ) : (
                <OfferCardComponent
                  onCardClicked={() => triggerOfferClickLog(offer)}
                  key={offer.id}
                  offer={offer}
                  viewType={adageViewType}
                />
              )}
              {adageViewType === 'list' && index === 0 && showDiffuseHelp ? (
                <HighlightBanner
                  title={'Le saviez-vous ?'}
                  description={
                    "Pour certaines offres, le pass Culture peut prendre en charge certains coûts accessoires nécessaires à la réalisation d'activités d'éducation artistique et culturelle menées en classe ou hors les murs. Cela peut inclure par exemple les frais de transport d’un intervenant ou le matériel consommable d’un atelier artistique. Cette prise en charge doit bien sûr faire l’objet d’un accord entre vous et le partenaire qui porte le projet. Il n’est en revanche pas possible d'acheter des livres ou des équipements pérennes avec les crédits pass Culture ou de financer le transport des élèves."
                  }
                  localStorageKey={'DIFFUSE_HELP_ADAGE_SEEN'}
                  img={
                    <ShadowTipsHelpIcon
                      className={styles['highlight-banner-icon']}
                    />
                  }
                  variant={HighlightBannerVariant.ADAGE}
                />
              ) : (
                adageViewType === 'list' &&
                index === 0 &&
                currentDate < highlightTargetDate && (
                  <HighlightBanner
                    title={"Permettre aux jeunes de s'exprimer par la danse"}
                    description={
                      "Du 23 juin au 10 août 2025, le pass Culture propose aux jeunes de 15 à 21 ans de participer au concours d'été de danse en filmant une chorégraphie dans la thématique des “soulèvements”. Des sélections de spectacles, livres, médias et vidéos d’artistes chorégraphes et danseurs seront diffusées sur l'application pour nourrir la créativité des jeunes."
                    }
                    localStorageKey={'TFD_2025_ADAGE_SEEN'}
                    img={
                      <img
                        src={TFD2025}
                        className={styles['banner']}
                        alt="Soulèvements"
                      />
                    }
                    cta={
                      <Button
                        as="a"
                        variant={ButtonVariant.PRIMARY}
                        to="https://passculture.docsend.com/view/nn7q3isav3dmhue2/d/pkhf9bba2ft4myz8"
                        isExternal
                        opensInNewTab
                        icon={fullLinkIcon}
                        onClick={() => logOpenHighlightBanner('TFD-2025')}
                        label="en savoir plus"
                      />
                    }
                    variant={HighlightBannerVariant.ADAGE}
                  />
                )
              )}
              {adageViewType === 'list' &&
                index === 1 &&
                showSurveySatisfaction && (
                  <SurveySatisfaction queryId={results.queryID} />
                )}
            </li>
          ))}
        </ul>
      </AccessibleScrollContainer>
      {!isInSuggestions && hits.length > 0 && (
        <div className={styles['pagination']}>
          <CustomPagination
            queryId={results.queryID}
            onPageChange={scrollToContentWrapper}
          />
        </div>
      )}
      {isBackToTopVisibile && (
        <a href="#root" className={styles['back-to-top-button']}>
          <SvgIcon
            alt=""
            src={fullGoTopIcon}
            className={styles['back-to-top-button-icon']}
            width="20"
          />
          Retour en haut
        </a>
      )}
    </>
  )
}
