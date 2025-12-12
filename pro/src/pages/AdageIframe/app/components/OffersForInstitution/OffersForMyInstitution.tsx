import useSWR from 'swr'

import { apiAdage } from '@/apiClient/api'
import { GET_COLLECTIVE_OFFERS_FOR_INSTITUTION_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeMyInstitution from '@/icons/stroke-my-institution.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { AdageOfferListCard } from '../OffersInstantSearch/OffersSearch/Offers/AdageOfferListCard/AdageOfferListCard'
import { AdageSkeleton } from '../Skeleton/AdageSkeleton'
import styles from './OffersForMyInstitution.module.scss'

export const OffersForMyInstitution = () => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')

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
    <>
      <h1 className={styles['title']}>Pour mon établissement</h1>
      <div className={styles['my-institution-callout']}>
        <Banner
          title="Processus de réservation"
          actions={[
            {
              href: `${document.referrer}adage/passculture/index`,
              isExternal: true,
              label: 'Voir la page “Suivi pass Culture”',

              icon: fullLinkIcon,
              iconAlt: 'Nouvelle fenêtre',
              type: 'link',
            },
          ]}
          description={
            <>
              <p className={styles['callout-text']}>
                Les offres de cette page sont destinées aux professeurs et
                co-construites avec les partenaires culturels.
              </p>
              <p>
                Pour réserver : 1) Préréservez l'offre, 2) Associez-la à un
                projet pédagogique dans "Les projets", 3) Le chef
                d'établissement validera dans "Suivi pass Culture".
              </p>
            </>
          }
        />
      </div>
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
              to={`/adage-iframe/recherche?token=${adageAuthToken}`}
              variant={ButtonVariant.PRIMARY}
            >
              Explorer le catalogue
            </ButtonLink>
          </div>
        </div>
      ) : (
        <ul className={styles['offers-list']}>
          {offers.collectiveOffers.map((offer) => {
            return (
              <li key={offer.id} data-testid="offer-listitem">
                <AdageOfferListCard offer={offer} />
              </li>
            )
          })}
        </ul>
      )}
    </>
  )
}
