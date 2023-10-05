import React, { useEffect, useState } from 'react'
import { useInfiniteHits, useStats } from 'react-instantsearch'

import { AdageFrontRoles } from 'apiClient/adage'
import useActiveFeature from 'hooks/useActiveFeature'
import fullGoTop from 'icons/full-go-top.svg'
import { getCollectiveOfferAdapter } from 'pages/AdageIframe/app/adapters/getCollectiveOfferAdapter'
import { getCollectiveOfferTemplateAdapter } from 'pages/AdageIframe/app/adapters/getCollectiveOfferTemplateAdapter'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
} from 'pages/AdageIframe/app/types/offers'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { DiffuseHelp } from '../../../DiffuseHelp/DiffuseHelp'
import { SurveySatisfaction } from '../../../SurveySatisfaction/SurveySatisfaction'

import { NoResultsPage } from './NoResultsPage/NoResultsPage'
import Offer from './Offer'
import styles from './Offers.module.scss'
import { extractOfferIdFromObjectId, offerIsBookable } from './utils'

export interface OffersProps {
  displayStats?: boolean
  logFiltersOnSearch?: (nbHits: number, queryId?: string) => void
  submitCount?: number
  isBackToTopVisibile?: boolean
}

type OfferMap = Map<
  string,
  HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
>

export const Offers = ({
  displayStats = true,
  logFiltersOnSearch,
  submitCount,
  isBackToTopVisibile = false,
}: OffersProps): JSX.Element => {
  const { hits, isLastPage, showMore, results } = useInfiniteHits()
  const { nbHits } = useStats()

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

  useEffect(() => {
    setQueriesAreLoading(true)
    if (logFiltersOnSearch) {
      logFiltersOnSearch(nbHits, results?.queryID)
    }

    Promise.all(
      hits.map(async hit => {
        if (fetchedOffers.has(hit.objectID)) {
          return Promise.resolve({
            hitId: hit.objectID,
            offer: fetchedOffers.get(hit.objectID),
          })
        }
        const offerId = extractOfferIdFromObjectId(hit.objectID)
        const { isOk, payload: offer } = await (hit.isTemplate
          ? getCollectiveOfferTemplateAdapter(offerId)
          : getCollectiveOfferAdapter(offerId))

        if (!isOk) {
          return { hitId: undefined, offer: undefined }
        }

        return { hitId: hit.objectID, offer }
      })
    )
      .then(offersFromHits => {
        const offersFromHitsMap = new Map(fetchedOffers)
        offersFromHits
          .filter(res => res?.offer && offerIsBookable(res.offer))
          .forEach(res => {
            if (res?.hitId && res.offer) {
              offersFromHitsMap.set(res.hitId, res.offer)
            }
          })
        setFetchedOffers(offersFromHitsMap)
      })
      .finally(() => {
        setQueriesAreLoading(false)
      })
  }, [results?.queryID])

  const offers = [...fetchedOffers.values()]

  if (queriesAreLoading && offers.length === 0) {
    return (
      <div className={styles['offers-loader']}>
        <Spinner message="Recherche en cours" />
      </div>
    )
  }

  if (hits?.length === 0 || offers.length === 0) {
    return <NoResultsPage query={results?.query} />
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
          <div key={`${offer.isTemplate ? 'T' : ''}${offer.id}`}>
            <Offer
              offer={offer}
              position={index}
              queryId={results?.queryID ?? ''}
            />
            {index === 0 && showDiffuseHelp && (
              <DiffuseHelp
                description={
                  "Pour certaines offres, le pass Culture peut prendre en charge certains coûts accessoires nécessaires à la réalisation d'activités d'éducation artistique et culturelle menées en classe ou hors les murs. Cela peut inclure par exemple les frais de transport d'un intervenant ou le matériel consommable d'un atelier artistique. Cette prise en charge doit bien sûr faire l'objet d'un accord entre vous et le partenaire qui porte le projet. Il n'est en revanche pas possible d'acheter des livres ou des équipements pérennes avec les crédits pass Culture ou de financer le transport des élèves."
                }
              />
            )}
            {index === 1 && showSurveySatisfaction && (
              <SurveySatisfaction queryId={results?.queryID} />
            )}
          </div>
        ))}
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
              <Button onClick={showMore} variant={ButtonVariant.SECONDARY}>
                Voir plus d’offres
              </Button>
            ))}
        </div>
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
