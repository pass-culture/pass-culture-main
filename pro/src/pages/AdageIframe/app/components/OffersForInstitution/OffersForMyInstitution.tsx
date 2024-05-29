import useSWR from 'swr'

import { apiAdage } from 'apiClient/api'
import { Callout } from 'components/Callout/Callout'
import { GET_COLLECTIVE_OFFERS_FOR_INSTITUTION_QUERY_KEY } from 'config/swrQueryKeys'
import { useActiveFeature } from 'hooks/useActiveFeature'
import strokeMyInstitution from 'icons/stroke-my-institution.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { AnalyticsContextProvider } from '../../providers/AnalyticsContextProvider'
import { AdageOfferListCard } from '../OffersInstantSearch/OffersSearch/Offers/AdageOfferListCard/AdageOfferListCard'
import { Offer } from '../OffersInstantSearch/OffersSearch/Offers/Offer'
import { AdageSkeleton } from '../Skeleton/AdageSkeleton'

import styles from './OffersForMyInstitution.module.scss'

export const OffersForMyInstitution = () => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')

  const isNewOfferCardEnabled = useActiveFeature(
    'WIP_ENABLE_ADAGE_VISUALIZATION'
  )

  const { data: offers, isLoading } = useSWR(
    [GET_COLLECTIVE_OFFERS_FOR_INSTITUTION_QUERY_KEY],
    () => apiAdage.getCollectiveOffersForMyInstitution(),
    { fallbackData: { collectiveOffers: [] } }
  )

  if (isLoading) {
    return (
      <>
        <AdageSkeleton />
        <AdageSkeleton />
        <AdageSkeleton />
      </>
    )
  }

  return (
    <AnalyticsContextProvider>
      <h1>Pour mon établissement</h1>
      <Callout
        className={styles['my-institution-callout']}
        links={[
          {
            href: `${document.referrer}adage/passculture/index`,
            isExternal: true,
            label: 'Voir la page “Suivi pass Culture”',
          },
        ]}
      >
        <p className={styles['callout-text']}>
          Retrouvez sur cette page les offres destinées aux professeurs de votre
          établissement et rédigées par les acteurs culturels partenaires de
          l’établissement scolaire.
        </p>
        <p className={styles['callout-text']}>
          Le contenu, la date et le montant de chaque offre ont été définis lors
          d’échanges entre un professeur et la structure culturelle concernée.
        </p>
        <p>
          Processus : vous cliquez sur “Préréserver” l’offre qui vous est
          destinée. L’offre va disparaitre de cette page, mais vous pourrez la
          retrouver dans la page “Suivi pass Culture”. Puis, vous associerez
          l’offre à votre projet pédagogique dans la page “Les projets”. Enfin,
          votre chef d’établissement confirmera la réservation de l’offre dans
          “Suivi pass Culture”.
        </p>
      </Callout>
      {offers.collectiveOffers.length === 0 ? (
        <div className={styles['no-results']}>
          <SvgIcon
            src={strokeMyInstitution}
            alt=""
            viewBox="0 0 375 154"
            width="375"
            className={styles['no-results-svg']}
          />
          <div>
            <h2 className={styles['no-results-title']}>
              Vous n’avez pas d’offre à préréserver
            </h2>
            <ButtonLink
              link={{
                to: `/adage-iframe/recherche?token=${adageAuthToken}`,
                isExternal: false,
              }}
              variant={ButtonVariant.PRIMARY}
            >
              Explorer le catalogue
            </ButtonLink>
          </div>
        </div>
      ) : (
        <ul className={styles['offers-list']}>
          {offers.collectiveOffers.map((offer, i) => {
            return (
              <li key={offer.id} data-testid="offer-listitem">
                {isNewOfferCardEnabled ? (
                  <AdageOfferListCard offer={offer} />
                ) : (
                  <Offer offer={offer} queryId="" position={i} />
                )}
              </li>
            )
          })}
        </ul>
      )}
    </AnalyticsContextProvider>
  )
}
