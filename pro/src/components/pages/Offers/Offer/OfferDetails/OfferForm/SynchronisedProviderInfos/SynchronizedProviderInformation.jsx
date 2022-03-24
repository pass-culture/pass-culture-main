import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { getProviderInfo } from 'components/pages/Offers/domain/getProviderInfo'

const SynchronizedProviderInformation = ({ providerName }) => {
  const providerInfo = getProviderInfo(providerName)

  return (
    <div className="provider-information">
      <Icon alt={providerInfo.name} svg={providerInfo.icon} />
      {providerInfo.synchronizedOfferMessage}
    </div>
  )
}

SynchronizedProviderInformation.propTypes = {
  providerName: PropTypes.string.isRequired,
}

export default SynchronizedProviderInformation
