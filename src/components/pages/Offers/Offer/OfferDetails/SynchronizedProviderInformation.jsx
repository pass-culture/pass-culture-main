import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { getProviderInfo } from 'components/pages/Offers/domain/getProviderInfo'

const SynchronizedProviderInformation = ({ providerName }) => {
  const providerInfo = getProviderInfo(providerName)

  return (
    <div className="provider-information">
      <Icon
        alt={`Icône de ${providerInfo.name}`}
        svg={providerInfo.icon}
      />
      {`Offre synchronisée avec ${providerInfo.name}`}
    </div>
  )
}

SynchronizedProviderInformation.propTypes = {
  providerName: PropTypes.string.isRequired,
}

export default SynchronizedProviderInformation
