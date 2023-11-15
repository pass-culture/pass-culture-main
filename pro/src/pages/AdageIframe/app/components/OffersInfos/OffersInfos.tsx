import React from 'react'

import { mockOffer } from '../AdageDiscovery/AdageDiscovery'
import Offer from '../OffersInstantSearch/OffersSearch/Offers/Offer'

import styles from './OffersInfos.module.scss'

export const OffersInfos = () => {
  return (
    <div className={styles['container']}>
      <Offer offer={mockOffer} position={0} queryId="" openDetails={true} />
    </div>
  )
}
