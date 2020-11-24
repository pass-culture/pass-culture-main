import PropTypes from 'prop-types'
import React, { useEffect } from 'react'
import ReactTooltip from 'react-tooltip'

import Icon from 'components/layout/Icon'
import Thumb from 'components/layout/Thumb'

import { synchronizableProviders } from '../enums'

const SynchronizableProviderInformation = props => {
  const { offer } = props
  const { lastProvider, thumbUrl, offererId, venueId } = offer
  const providerName = lastProvider.name.toLowerCase()
  const providerInfo = synchronizableProviders[providerName]

  useEffect(() => {
    ReactTooltip.rebuild()
  }, [])

  const tooltip = (
    <div>
      <p>
        {'Vous pouvez modifier vos choix de synchronisation sur'}
        <a href={`/structures/${offererId}/lieux/${venueId}`}>
          {'la page du lieu'}
        </a>
        {'qui présente cette offre, dans la section "Importation d’offres".'}
      </p>
    </div>
  )

  return (
    <div className="provider-information">
      <div className="provider-thumb">
        <Thumb url={thumbUrl} />
      </div>
      <div className="provider-details">
        <div className="provider-header">
          <Icon
            height="64px"
            svg={providerInfo.icon}
            width="64px"
          />
          <div className="provider-title">
            <h3>
              {`Offre synchronisée avec ${providerInfo.name}`}
            </h3>
            <span
              className="button"
              data-place="bottom"
              data-tip={tooltip}
              data-type="info"
            >
              <Icon svg="picto-info" />
            </span>
          </div>
        </div>
        <p className="provider-explanation">
          {`Le visuel par défaut, les informations et le stock de cette offre sont synchronisés avec les données ${providerInfo.name} tous les soirs.`}
        </p>
      </div>
    </div>
  )
}

SynchronizableProviderInformation.propTypes = {
  offer: PropTypes.shape().isRequired,
}

export default SynchronizableProviderInformation
