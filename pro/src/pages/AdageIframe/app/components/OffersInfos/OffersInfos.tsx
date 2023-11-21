import React from 'react'
import { useSearchParams } from 'react-router-dom'

import Breadcrumb from 'components/Breadcrumb/Breadcrumb'
import strokePassIcon from 'icons/stroke-pass.svg'

import { mockOffer } from '../AdageDiscovery/AdageDiscovery'
import Offer from '../OffersInstantSearch/OffersSearch/Offers/Offer'

import styles from './OffersInfos.module.scss'

export const OffersInfos = () => {
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
                to: `/adage-iframe/decouverte?token=${adageAuthToken}`,
              },
              icon: strokePassIcon,
            },
            {
              title: mockOffer.name,
              link: {
                isExternal: true,
                to: '#',
              },
            },
          ]}
        />
      </div>
      <Offer offer={mockOffer} position={0} queryId="" openDetails={true} />
    </div>
  )
}
