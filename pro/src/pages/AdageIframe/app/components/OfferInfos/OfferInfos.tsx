import React, { useEffect, useState } from 'react'
import { useLocation, useParams, useSearchParams } from 'react-router-dom'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import Breadcrumb, { Crumb } from 'components/Breadcrumb/Breadcrumb'
import strokePassIcon from 'icons/stroke-pass.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import useAdageUser from '../../hooks/useAdageUser'
import Offer from '../OffersInstantSearch/OffersSearch/Offers/Offer'

import offerInfosFallback from './assets/offer-infos-fallback.svg'
import styles from './OfferInfos.module.scss'

export const OfferInfos = () => {
  const { state } = useLocation()
  const { offerId } = useParams()

  const [offer, setOffer] = useState(state?.offer)
  const [loading, setLoading] = useState(false)

  const { adageUser } = useAdageUser()

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

  const [searchParams] = useSearchParams()
  const adageAuthToken = searchParams.get('token')

  if (loading) {
    return <Spinner />
  }

  const originCrumb: Crumb = {
    title:
      adageUser.role === AdageFrontRoles.READONLY ? 'Recherche' : 'Découvrir',
    link: {
      isExternal: false,
      to:
        adageUser.role === AdageFrontRoles.READONLY
          ? `/adage-iframe/recherche?token=${adageAuthToken}`
          : `/adage-iframe/decouverte?token=${adageAuthToken}`,
    },
    icon:
      adageUser.role === AdageFrontRoles.READONLY
        ? strokeSearchIcon
        : strokePassIcon,
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
