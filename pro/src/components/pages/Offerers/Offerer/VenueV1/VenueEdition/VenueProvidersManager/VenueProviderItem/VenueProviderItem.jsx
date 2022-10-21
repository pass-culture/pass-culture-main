import './VenueProviderItem.scss'

import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { isAllocineProvider, isCinemaProvider } from 'core/Providers'
import { getProviderInfo } from 'core/Providers/utils'
import { ReactComponent as IconOffers } from 'icons/ico-offers.svg'
import { pluralize } from 'utils/pluralize'
import { formatLocalTimeDateString } from 'utils/timezone'

const VenueProviderItem = ({
  venueProvider,
  venueDepartmentCode,
  children,
}) => {
  const { lastSyncDate, nOffers, provider, venueIdAtOfferProvider } =
    venueProvider
  const providerInfo = getProviderInfo(provider.name)
  const shouldDisplayProviderInformations =
    isAllocineProvider(provider) || isCinemaProvider(provider) || lastSyncDate

  return (
    <li className="venue-provider-row">
      <div className="venue-provider-item-info">
        {!!providerInfo && (
          <Icon height="64px" svg={providerInfo.icon} width="64px" />
        )}

        <div className="provider-name-container">
          {
            /* istanbul ignore next: DEBT, TO FIX */
            providerInfo?.name ?? provider.name
          }
        </div>

        {!lastSyncDate ? (
          <div className="venue-id-at-offer-provider-container-with-message">
            <div className="venue-id-at-offer-provider">
              {'Compte : '}
              <strong>{venueIdAtOfferProvider}</strong>
            </div>
            <div className="import-label-container">
              {'Importation en cours.' +
                ' Cette étape peut durer plusieurs dizaines de minutes.' +
                ' Vous pouvez fermer votre navigateur et revenir plus tard.'}
            </div>
          </div>
        ) : (
          <div className="venue-id-at-offer-provider-container">
            <div className="venue-id-at-offer-provider">
              {'Compte : '}
              <strong>{venueIdAtOfferProvider}</strong>
            </div>
            <div className="offers-container-counter">
              <IconOffers className="offers-counter-icon" />
              <div className="number-of-offers-label">
                {pluralize(nOffers, 'offres')}
              </div>
            </div>
          </div>
        )}
      </div>
      {shouldDisplayProviderInformations && (
        <div className="venue-informations">
          <ul>
            {lastSyncDate && (
              <li className="venue-informations-sync-item">
                <span>{'Dernière synchronisation : '}</span>
                <span data-testid="last-sync-date">
                  &nbsp;
                  {formatLocalTimeDateString(
                    lastSyncDate,
                    venueDepartmentCode,
                    'dd/MM/yyyy à HH:mm'
                  )}
                </span>
              </li>
            )}
            {children}
          </ul>
        </div>
      )}
    </li>
  )
}

VenueProviderItem.defaultProps = {
  children: null,
}

VenueProviderItem.propTypes = {
  children: PropTypes.node,
  venueDepartmentCode: PropTypes.string.isRequired,
  venueProvider: PropTypes.shape({
    provider: PropTypes.shape({
      name: PropTypes.string.isRequired,
    }).isRequired,
    lastSyncDate: PropTypes.string,
    nOffers: PropTypes.number.isRequired,
    venueIdAtOfferProvider: PropTypes.string,
  }).isRequired,
}

export default VenueProviderItem
