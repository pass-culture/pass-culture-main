import React from 'react'

import { getProviderInfo } from 'core/Providers'
import Banner from 'ui-kit/Banners/Banner'
import Icon from 'ui-kit/Icon/Icon'

import styles from './SynchronizedProviderInformation.module.scss'

export interface ISynchronizedProviderInformation {
  providerName: string
}

const SynchronizedProviderInformation = ({
  providerName,
}: ISynchronizedProviderInformation): JSX.Element | null => {
  const providerInfo = getProviderInfo(providerName)
  if (providerInfo === undefined) {
    return null
  }

  return (
    <div
      className="provider-information"
      data-testid="synchronized-provider-information"
    >
      <Banner
        type="notification-info"
        showTitle={false}
        className={styles['banner-provider']}
        isProvider
      >
        <Icon
          alt={providerInfo.name}
          svg={providerInfo.icon}
          className={styles['provider-logo']}
        />
        <span>{providerInfo.synchronizedOfferMessage}</span>
      </Banner>
    </div>
  )
}

export default SynchronizedProviderInformation
