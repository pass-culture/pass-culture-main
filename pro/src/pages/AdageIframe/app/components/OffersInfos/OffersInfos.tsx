import React, { useEffect, useState } from 'react'
import { useLocation, useParams, useSearchParams } from 'react-router-dom'

import { apiAdage } from 'apiClient/api'
import Breadcrumb from 'components/Breadcrumb/Breadcrumb'
import strokePassIcon from 'icons/stroke-pass.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import Offer from '../OffersInstantSearch/OffersSearch/Offers/Offer'

import styles from './OffersInfos.module.scss'

export const OffersInfos = () => {
  const { state } = useLocation()
  const { offerId } = useParams()

  const [offer, setOffer] = useState(state?.offer)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function getOffer() {
      setLoading(true)
      try {
        const fetchedOffer = await apiAdage.getCollectiveOfferTemplate(
          Number(offerId)
        )
        setOffer(fetchedOffer)
      } catch {
        setOffer(null)
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

  return (
    <div className={styles['offers-info']}>
      {offer ? (
        <>
          <div className={styles['offers-info-breadcrumb']}>
            <Breadcrumb
              crumbs={[
                {
                  title: 'Découvrir',
                  link: {
                    isExternal: false,
                    to: `/adage-iframe?token=${adageAuthToken}`,
                  },
                  icon: strokePassIcon,
                },
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
              <path
                fill="currentColor"
                d="M70 28.9a6.3 6.3 0 0 0-6.4 6.3v101.3c0 3.5 2.9 6.4 6.4 6.4h44.3a33.3 33.3 0 0 1 46.1-42.9c1.3.7 1.8 2.3 1 3.5a2.7 2.7 0 0 1-3.5 1.1 28 28 0 1 0 11.5 11.3 2.6 2.6 0 0 1 1-3.5c1.3-.7 2.9-.2 3.6 1a33.3 33.3 0 0 1-56.2 35.5c-.4.2-.8.3-1.3.3H70c-7 0-12.7-5.6-12.7-12.7V35.2c0-7 5.7-12.7 12.7-12.7h57.2c7 0 12.6 5.7 12.6 12.7v52.4a3.2 3.2 0 1 1-6.3 0V35.2c0-3.5-2.8-6.3-6.3-6.3H70Zm77.2 3.9c-.5 1.7.6 3.4 2.2 3.8l20.3 5.4c3.3.9 5.3 4.3 4.4 7.7l-9.8 38.6c-.4 1.7.6 3.5 2.3 4 1.6.4 3.4-.6 3.8-2.3l9.8-38.6a12.6 12.6 0 0 0-9-15.6L151 30.5c-1.7-.4-3.4.6-3.8 2.3Zm-11 83.8a3 3 0 0 0-4.2 0 3 3 0 0 0 0 4.3l8.4 8.4-8.3 8.4a3 3 0 0 0 0 4.2 3 3 0 0 0 4.2 0l8.4-8.4 8.4 8.4a3 3 0 0 0 4.3 0 3 3 0 0 0 0-4.3l-8.4-8.3 8.3-8.4a3 3 0 0 0 0-4.2 3 3 0 0 0-4.2 0l-8.4 8.3-8.4-8.4Z"
              />
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
