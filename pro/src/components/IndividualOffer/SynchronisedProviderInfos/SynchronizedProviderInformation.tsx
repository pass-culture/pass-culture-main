import { getProviderInfo } from 'commons/core/Providers/utils/getProviderInfo'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import styles from './SynchronizedProviderInformation.module.scss'

export interface SynchronizedProviderInformationProps {
  providerName: string
}

export const SynchronizedProviderInformation = ({
  providerName,
}: SynchronizedProviderInformationProps): JSX.Element | null => {
  const providerInfo = getProviderInfo(providerName)
  if (providerInfo === undefined) {
    return null
  }

  return (
    <Callout variant={CalloutVariant.INFO}>
      <div className={styles['banner-content']}>
        {providerInfo.logo && (
          <img
            alt={providerInfo.name}
            src={providerInfo.logo}
            className={styles['provider-logo']}
          />
        )}
        <p className={!providerInfo.logo ? styles['provider-text'] : ''}>
          {providerInfo.synchronizedOfferMessage}
        </p>
      </div>
    </Callout>
  )
}
