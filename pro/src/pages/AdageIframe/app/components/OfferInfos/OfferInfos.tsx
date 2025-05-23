import { useLocation, useParams, useSearchParams } from 'react-router'
import useSWR from 'swr'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import strokePassIcon from 'icons/stroke-pass.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import strokeStarIcon from 'icons/stroke-star.svg'
import strokeVenueIcon from 'icons/stroke-venue.svg'
import { Breadcrumb, Crumb } from 'ui-kit/Breadcrumb/Breadcrumb'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { useAdageUser } from '../../hooks/useAdageUser'

import { AdageOffer } from './AdageOffer/AdageOffer'
import offerInfosFallback from './assets/offer-infos-fallback.svg'
import styles from './OfferInfos.module.scss'

export const OfferInfos = () => {
  const { state, pathname } = useLocation()
  const { offerId: offerIdInParams } = useParams()
  const [searchParams] = useSearchParams()
  const adageAuthToken = searchParams.get('token')

  const parentRouteInUrl = pathname.split('/')[2] ?? 'recherche'

  const isOfferTemplate = !offerIdInParams?.startsWith('B-')
  //  Bookable offers ids are prefixed with B- while template offers ids are prefixed with T-, or not prefixed for legacy reasons.
  const offerId = offerIdInParams?.split('-')[1] ?? offerIdInParams

  const { adageUser, setInstitutionOfferCount, institutionOfferCount } =
    useAdageUser()

  const shouldFetchTemplateOffer = isOfferTemplate && !state?.offer && offerId
  const { data: templateOffer, isLoading: isTemplateOfferLoading } = useSWR(
    shouldFetchTemplateOffer
      ? [GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY, Number(offerId)]
      : null,
    ([, offerIdParam]) => apiAdage.getCollectiveOfferTemplate(offerIdParam)
  )

  const shouldFetchBookableOffer = !isOfferTemplate && !state?.offer && offerId
  const { data: bookableOffer, isLoading: isBookableOfferLoading } = useSWR(
    shouldFetchBookableOffer
      ? [GET_COLLECTIVE_OFFER_QUERY_KEY, Number(offerId)]
      : null,
    ([, offerIdParam]) => apiAdage.getCollectiveOffer(offerIdParam)
  )

  const offer = state?.offer ?? templateOffer ?? bookableOffer

  const crumbForCurrentRoute: { [key: string]: Crumb } = {
    recherche: {
      title: 'Recherche',
      link: {
        isExternal: false,
        to: `/adage-iframe/recherche?token=${adageAuthToken}`,
      },
      icon: strokeSearchIcon,
    },
    decouverte: {
      title: 'Découvrir',
      link: {
        isExternal: false,
        to: `/adage-iframe/decouverte?token=${adageAuthToken}`,
      },
      icon: strokePassIcon,
    },
    ['mes-favoris']: {
      title: 'Mes favoris',
      link: {
        isExternal: false,
        to: `/adage-iframe/mes-favoris?token=${adageAuthToken}`,
      },
      icon: strokeStarIcon,
    },
    ['mon-etablissement']: {
      title: 'Pour mon établissement',
      link: {
        isExternal: false,
        to: `/adage-iframe/mon-etablissement?token=${adageAuthToken}`,
      },
      icon: strokeVenueIcon,
    },
  }

  const originCrumb: Crumb = isOfferTemplate
    ? crumbForCurrentRoute[
        adageUser.role === AdageFrontRoles.READONLY
          ? 'recherche'
          : parentRouteInUrl
      ]
    : crumbForCurrentRoute['mon-etablissement']

  if (isTemplateOfferLoading || isBookableOfferLoading) {
    return <Spinner />
  }

  return (
    <div className={styles['offers-info']}>
      {offer ? (
        <>
          <div className={styles['offers-info-breadcrumb']}>
            <Breadcrumb
              crumbs={[
                originCrumb,
                {
                  title: offer.name,
                  link: {
                    isExternal: true,
                    to: '#',
                  },
                },
              ]}
            />
          </div>
          <AdageOffer
            offer={offer}
            adageUser={adageUser}
            setInstitutionOfferCount={setInstitutionOfferCount}
            institutionOfferCount={institutionOfferCount}
            playlistId={state?.playlistId}
          />
        </>
      ) : (
        <div className={styles['offers-info-fallback']}>
          <div className={styles['offers-info-fallback-svg']}>
            <svg xmlns="http://www.w3.org/2000/svg" width="238" height="185">
              <use xlinkHref={`${offerInfosFallback}#path`} />
            </svg>
          </div>
          <h1 className={styles['offers-info-fallback-title']}>
            Cette offre est introuvable
          </h1>
          <ButtonLink
            to={`/adage-iframe/recherche?token=${adageAuthToken}`}
            variant={ButtonVariant.PRIMARY}
          >
            Explorer le catalogue
          </ButtonLink>
        </div>
      )}
    </div>
  )
}
