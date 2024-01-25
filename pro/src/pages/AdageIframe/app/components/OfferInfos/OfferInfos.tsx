import React, { useEffect, useState } from 'react'
import { useLocation, useParams, useSearchParams } from 'react-router-dom'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import Breadcrumb, { Crumb } from 'components/Breadcrumb/Breadcrumb'
import strokePassIcon from 'icons/stroke-pass.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import strokeStarIcon from 'icons/stroke-star.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import useAdageUser from '../../hooks/useAdageUser'
import Offer from '../OffersInstantSearch/OffersSearch/Offers/Offer'

import offerInfosFallback from './assets/offer-infos-fallback.svg'
import styles from './OfferInfos.module.scss'

export const OfferInfos = () => {
  const { state, pathname } = useLocation()
  const { offerId } = useParams()
  const [searchParams] = useSearchParams()
  const adageAuthToken = searchParams.get('token')

  const parentRouteInUrl = pathname.split('/')[2] ?? 'recherche'

  const [offer, setOffer] = useState(state?.offer)
  const [loading, setLoading] = useState(false)

  const { adageUser } = useAdageUser()

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
  }

  const originCrumb: Crumb =
    crumbForCurrentRoute[
      adageUser.role === AdageFrontRoles.READONLY
        ? 'recherche'
        : parentRouteInUrl
    ]

  useEffect(() => {
    async function getOffer() {
      setLoading(true)
      try {
        const fetchedOffer = await apiAdage.getCollectiveOfferTemplate(
          Number(offerId)
        )
        setOffer(fetchedOffer)
      } finally {
        setLoading(false)
      }
    }

    if (!state?.offer && offerId) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      getOffer()
    }
  }, [offerId, state?.offer])

  if (loading) {
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
          <Offer
            offer={{ ...offer, isTemplate: true }}
            position={0}
            queryId=""
            openDetails={true}
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
            link={{
              isExternal: false,
              to: `/adage-iframe/recherche?token=${adageAuthToken}`,
            }}
            variant={ButtonVariant.PRIMARY}
          >
            Explorer le catalogue
          </ButtonLink>
        </div>
      )}
    </div>
  )
}
