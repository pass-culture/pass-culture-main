import { useEffect } from 'react'
import {
  useInfiniteHits,
  useInstantSearch,
  useStats,
} from 'react-instantsearch'
import { useDispatch, useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'
import useSWR from 'swr'

import {
  AdageFrontRoles,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  VenueResponse,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { GET_COLLECTIVE_OFFER_TEMPLATES_QUERY_KEY } from 'config/swrQueryKeys'
import useActiveFeature from 'hooks/useActiveFeature'
import { useMediaQuery } from 'hooks/useMediaQuery'
import fullGoTop from 'icons/full-go-top.svg'
import fullGrid from 'icons/full-grid.svg'
import fullList from 'icons/full-list.svg'
import { useAdageUser } from 'pages/AdageIframe/app/hooks/useAdageUser'
import { isCollectiveOfferTemplate } from 'pages/AdageIframe/app/types'
import { setSearchView } from 'store/adageFilter/reducer'
import { adageSearchViewSelector } from 'store/adageFilter/selectors'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { LOGS_DATA } from 'utils/config'

import { OfferCardComponent } from '../../../AdageDiscovery/OfferCard/OfferCard'
import { DiffuseHelp } from '../../../DiffuseHelp/DiffuseHelp'
import { CustomPagination } from '../../../Pagination/Pagination'
import { AdageSkeleton } from '../../../Skeleton/AdageSkeleton'
import { SurveySatisfaction } from '../../../SurveySatisfaction/SurveySatisfaction'
import {
  ToggleButtonGroup,
  ToggleButton,
} from '../../../ToggleButtonGroup/ToggleButtonGroup'

import { AdageOfferListCard } from './AdageOfferListCard/AdageOfferListCard'
import { NoResultsPage } from './NoResultsPage/NoResultsPage'
import { Offer } from './Offer'
import styles from './Offers.module.scss'
import { offerIsBookable } from './utils/offerIsBookable'

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
  const dispatch = useDispatch()

  const adageViewType = useSelector(adageSearchViewSelector)
  const { currentPageHits: hits } = useInfiniteHits()
  const { nbHits } = useStats()
  const { scopedResults, results: nonScopedResult } = useInstantSearch()

  const isMobileScreen = useMediaQuery('(max-width: 46.5rem)')

  const location = useLocation()

  const isNewOfferCardEnabled = useActiveFeature(
    'WIP_ENABLE_ADAGE_VISUALIZATION'
  )

  const results = indexId
    ? scopedResults.find((res) => res.indexId === indexId)?.results
    : nonScopedResult

  const showDiffuseHelp = (submitCount ?? 0) > 0

  const isInSuggestions = indexId?.startsWith('no_results_offers')

  const { adageUser } = useAdageUser()

  const showSurveySatisfaction =
    !adageUser.preferences?.feedback_form_closed &&
    adageUser.role !== AdageFrontRoles.READONLY

  const hitsIds = hits.map((hit) => Number(hit.objectID.split('-')[1]))
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
    .filter(
      (offer): offer is CollectiveOfferTemplateResponseModel =>
        !!offer && offerIsBookable(offer)
    )

  useEffect(() => {
    isMobileScreen && dispatch(setSearchView('grid'))
  }, [isMobileScreen, dispatch])

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
    dispatch(setSearchView(viewType))
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    apiAdage.logOfferListViewSwitch({
      iframeFrom: location.pathname,
      source: viewType,
    })
  }

  function triggerOfferClickLog(
    offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  ) {
    if (!LOGS_DATA) {
      return
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    apiAdage.logOfferTemplateDetailsButtonClick({
      iframeFrom: location.pathname,
      offerId: isCollectiveOfferTemplate(offer) ? offer.id : offer.stock.id,
      queryId: results?.queryID,
      isFromNoResult: isInSuggestions,
      vueType: adageViewType,
    })
  }

  return (
    <>
      <div className={styles['offers-view']}>
        {displayStats && (
          <div className={styles['offers-stats']}>
            {new Intl.NumberFormat('fr-FR').format(nbHits)}{' '}
            {nbHits === 1 ? 'offre' : 'offres'} au total
          </div>
        )}
        {isNewOfferCardEnabled && !isInSuggestions && (
          <ToggleButtonGroup
            className={styles['offer-type-vue']}
            groupLabel="Choix du type de vue des offres"
            buttons={[
              {
                label: 'Vue liste',
                id: 'list',
                content: <SvgIcon width="24" src={fullList} alt="" />,
                onClick: toggleButtonClicked,
              },
              {
                label: 'Vue grille',
                id: 'grid',
                content: <SvgIcon width="24" src={fullGrid} alt="" />,
                onClick: toggleButtonClicked,
              },
            ]}
            activeButton={adageViewType}
          />
        )}
      </div>
      <ul
        className={
          styles[
            `offers-${!isNewOfferCardEnabled || isInSuggestions ? 'list' : adageViewType}`
          ]
        }
      >
        {offers.map((offer, index) => (
          <li
            key={`${offer.isTemplate ? 'T' : ''}${offer.id}`}
            data-testid="offer-listitem"
          >
            {isNewOfferCardEnabled ? (
              adageViewType === 'list' || isInSuggestions ? (
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
              )
            ) : (
              <Offer
                offer={offer}
                position={index}
                queryId={results.queryID ?? ''}
                isInSuggestions={indexId?.startsWith('no_results_offers')}
              />
            )}
            {adageViewType === 'list' && index === 0 && showDiffuseHelp && (
              <DiffuseHelp
                description={
                  "Pour certaines offres, le pass Culture peut prendre en charge certains coûts accessoires nécessaires à la réalisation d'activités d'éducation artistique et culturelle menées en classe ou hors les murs. Cela peut inclure par exemple les frais de transport d’un intervenant ou le matériel consommable d’un atelier artistique. Cette prise en charge doit bien sûr faire l’objet d’un accord entre vous et le partenaire qui porte le projet. Il n’est en revanche pas possible d'acheter des livres ou des équipements pérennes avec les crédits pass Culture ou de financer le transport des élèves."
                }
              />
            )}
            {adageViewType === 'list' &&
              index === 1 &&
              showSurveySatisfaction && (
                <SurveySatisfaction queryId={results.queryID} />
              )}
          </li>
        ))}
      </ul>
      {!isInSuggestions && hits.length > 0 && (
        <div className={styles['pagination']}>
          <CustomPagination queryId={results.queryID} />
        </div>
      )}
      {isBackToTopVisibile && (
        <a href="#root" className={styles['back-to-top-button']}>
          <SvgIcon
            alt=""
            src={fullGoTop}
            className={styles['back-to-top-button-icon']}
            width="20"
          />
          Retour en haut
        </a>
      )}
    </>
  )
}
