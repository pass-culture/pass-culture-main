import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { getProviderInfo } from 'core/Providers/utils'

export interface ISynchronizedProviderInformation {
  providerName: string
}

const SynchronizedProviderInformation = ({
  providerName,
}: ISynchronizedProviderInformation): JSX.Element | null => {
  const providerInfo = getProviderInfo(providerName)

  if (providerInfo === undefined) return null

  return (
    <div
      className="provider-information"
      data-testid="synchronized-provider-information"
    >
      <Icon alt={providerInfo.name} svg={providerInfo.icon} />
      {providerInfo.synchronizedOfferMessage}
    </div>
  )
}

SynchronizedProviderInformation.propTypes = {
  providerName: PropTypes.string.isRequired,
}

export default SynchronizedProviderInformation
