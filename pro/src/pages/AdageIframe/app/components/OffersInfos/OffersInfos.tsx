import React from 'react'
import { useLocation, useSearchParams } from 'react-router-dom'

import Breadcrumb from 'components/Breadcrumb/Breadcrumb'
import strokePassIcon from 'icons/stroke-pass.svg'

import Offer from '../OffersInstantSearch/OffersSearch/Offers/Offer'

import styles from './OffersInfos.module.scss'

export const OffersInfos = () => {
  const {
    state: { offer: offer },
  } = useLocation()

  console.log('ici', useLocation())
  const [searchParams] = useSearchParams()
  const adageAuthToken = searchParams.get('token')

  return (
    <div className={styles['offers-info']}>
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
    </div>
  )
}
