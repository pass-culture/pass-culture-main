import React from 'react'

import { getProviderInfo } from 'core/Providers'
import { Banner } from 'ui-kit'

import styles from './SynchronizedProviderInformation.module.scss'

export interface SynchronizedProviderInformationProps {
  providerName: string
}

const SynchronizedProviderInformation = ({
  providerName,
}: SynchronizedProviderInformationProps): JSX.Element | null => {
  const providerInfo = getProviderInfo(providerName)
  if (providerInfo === undefined) {
    return null
  }

  return (
    <Banner
      type="notification-info"
      showTitle={false}
      className={styles['banner-provider']}
      isProvider
    >
      {providerInfo.logo && (
        <img
          alt={providerInfo.name}
          src={providerInfo.logo}
          className={styles['provider-logo']}
        />
      )}

      <span className={!providerInfo.logo ? styles['provider-text'] : ''}>
        {providerInfo.synchronizedOfferMessage}
      </span>
    </Banner>
  )
}

export default SynchronizedProviderInformation
