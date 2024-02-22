import React, { useEffect, useState } from 'react'
import {
  useInfiniteHits,
  useInstantSearch,
  useStats,
} from 'react-instantsearch'
import { useParams } from 'react-router-dom'

import {
  AdageFrontRoles,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  VenueResponse,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import useActiveFeature from 'hooks/useActiveFeature'
import fullGoTop from 'icons/full-go-top.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

import { DiffuseHelp } from '../../../DiffuseHelp/DiffuseHelp'
import { SurveySatisfaction } from '../../../SurveySatisfaction/SurveySatisfaction'

import { NoResultsPage } from './NoResultsPage/NoResultsPage'
import Offer from './Offer'
import styles from './Offers.module.scss'
import { extractOfferIdFromObjectId, offerIsBookable } from './utils'

export interface OffersProps {
  displayStats?: boolean
  displayShowMore?: boolean
  displayNoResult?: boolean
  logFiltersOnSearch?: (nbHits: number, queryId?: string) => void
  submitCount?: number
  isBackToTopVisibile?: boolean
  indexId?: string //  IndexId is necessary if the component is within the scope of a react-instantsearch <Index />
  venue?: VenueResponse | null
}

type CollectiveOffer =
  | CollectiveOfferResponseModel
  | CollectiveOfferTemplateResponseModel
type OfferMap = Map<string, CollectiveOffer>

export const Offers = ({
  displayStats = true,
  displayShowMore = true,
  displayNoResult = true,
  logFiltersOnSearch,
  submitCount,
  isBackToTopVisibile = false,
  indexId,
  venue,
}: OffersProps): JSX.Element | null => {
  const { hits, isLastPage, showMore } = useInfiniteHits()
  const { nbHits } = useStats()
  const { scopedResults, results: nonScopedResult } = useInstantSearch()
  const { siret, venueId } = useParams<{
    siret: string
    venueId: string
  }>()

  const results = indexId
    ? scopedResults.find((res) => res.indexId === indexId)?.results
    : nonScopedResult

  const [queriesAreLoading, setQueriesAreLoading] = useState(false)
  const [fetchedOffers, setFetchedOffers] = useState<OfferMap>(new Map())
  const isSatisfactionSurveyActive = useActiveFeature(
    'WIP_ENABLE_SATISFACTION_SURVEY'
  )
  const isDiffuseHelpActive = useActiveFeature('WIP_ENABLE_DIFFUSE_HELP')

  const showDiffuseHelp = isDiffuseHelpActive && (submitCount ?? 0) > 0

  const { adageUser } = useAdageUser()

  const showSurveySatisfaction =
    isSatisfactionSurveyActive &&
    !adageUser.preferences?.feedback_form_closed &&
    adageUser.role !== AdageFrontRoles.READONLY

  const showMoreAndTrack = async () => {
    showMore()

    await apiAdage.logSearchShowMore({
      iframeFrom: location.pathname,
      source: siret || venueId ? 'partnersMap' : 'homepage',
      queryId: results?.queryID,
    })
  }

  useEffect(() => {
    setQueriesAreLoading(true)
    if (logFiltersOnSearch) {
      logFiltersOnSearch(nbHits, results?.queryID)
    }

    Promise.allSettled(
      hits.map(
        async (hit): Promise<{ hitId?: string; offer?: CollectiveOffer }> => {
          if (fetchedOffers.has(hit.objectID)) {
            return {
              hitId: hit.objectID,
              offer: fetchedOffers.get(hit.objectID),
            }
          }
          const offerId = extractOfferIdFromObjectId(hit.objectID)

          try {
            if (hit.isTemplate) {
              const offer = await apiAdage.getCollectiveOfferTemplate(offerId)
              return {
                hitId: hit.objectID,
                offer: { ...offer, isTemplate: true },
              }
            } else {
              const offer = await apiAdage.getCollectiveOffer(offerId)
              return {
                hitId: hit.objectID,
                offer: { ...offer, isTemplate: false },
              }
            }
          } catch (e) {
            sendSentryCustomError(
              `error when retrieving adage offer ${hit.objectID} ${e}`
            )

            return {}
          }
        }
      )
    )
      .then((offersFromHits) => {
        const offersFromHitsMap = new Map(fetchedOffers)
        offersFromHits
          .filter(
            (res) =>
              res.status === 'fulfilled' &&
              res.value.offer &&
              offerIsBookable(res.value.offer)
          )
          .forEach((res) => {
            if (
              res.status === 'fulfilled' &&
              res.value.hitId &&
              res.value.offer
            ) {
              offersFromHitsMap.set(res.value.hitId, res.value.offer)
            }
          })
        setFetchedOffers(offersFromHitsMap)
      })
      .catch((e) => {
        sendSentryCustomError(
          `error when filtering offer results ${e}`,
          'data-processing'
        )
      })
      .finally(() => {
        setQueriesAreLoading(false)
      })
  }, [results?.queryID])

  const offers = hits
    .map((hit) => fetchedOffers.get(hit.objectID))
    .filter((offer): offer is CollectiveOffer => !!offer)

  if (queriesAreLoading && offers.length === 0) {
    return (
      <div className={styles['offers-loader']}>
        <Spinner message="Recherche en cours" />
      </div>
    )
  }

  if (hits?.length === 0 || offers.length === 0 || !results) {
    return displayNoResult ? (
      <NoResultsPage query={results?.query} venue={venue} />
    ) : null
  }

  return (
    <>
      {displayStats && (
        <div className={styles['offers-stats']}>
          {`${nbHits} résultat${nbHits > 1 ? 's' : ''}`}
        </div>
      )}
      <ul className={styles['offers-list']}>
        {offers.map((offer, index) => (
          <li
            key={`${offer.isTemplate ? 'T' : ''}${offer.id}`}
            data-testid="offer-listitem"
          >
            <Offer
              offer={offer}
              position={index}
              queryId={results?.queryID ?? ''}
              isInSuggestions={indexId?.startsWith('no_results_offers')}
            />
            {index === 0 && showDiffuseHelp && (
              <DiffuseHelp
                description={
                  "Pour certaines offres, le pass Culture peut prendre en charge certains coûts accessoires nécessaires à la réalisation d'activités d'éducation artistique et culturelle menées en classe ou hors les murs. Cela peut inclure par exemple les frais de transport d’un intervenant ou le matériel consommable d’un atelier artistique. Cette prise en charge doit bien sûr faire l’objet d’un accord entre vous et le partenaire qui porte le projet. Il n’est en revanche pas possible d'acheter des livres ou des équipements pérennes avec les crédits pass Culture ou de financer le transport des élèves."
                }
              />
            )}
            {index === 1 && showSurveySatisfaction && (
              <SurveySatisfaction queryId={results?.queryID} />
            )}
          </li>
        ))}
        {displayShowMore && (
          <div className={styles['offers-load-more']}>
            <div className={styles['offers-load-more-text']}>
              {!isLastPage
                ? `Vous avez vu ${offers.length} offre${
                    offers.length > 1 ? 's' : ''
                  } sur ${nbHits}`
                : 'Vous avez vu toutes les offres qui correspondent à votre recherche.'}
            </div>
            {!isLastPage &&
              (queriesAreLoading ? (
                <div className={styles['offers-loader']}>
                  <Spinner />
                </div>
              ) : (
                <Button
                  onClick={showMoreAndTrack}
                  variant={ButtonVariant.SECONDARY}
                >
                  Voir plus d’offres
                </Button>
              ))}
          </div>
        )}
      </ul>
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
