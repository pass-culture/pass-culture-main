import cn from 'classnames'
import React from 'react'

import { GetVenueResponseModel, VenueProviderResponse } from 'apiClient/v1'
import { getProviderInfo } from 'core/Providers/utils/getProviderInfo'
import {
  isAllocineProvider,
  isCinemaProvider,
} from 'core/Providers/utils/utils'
import { useWithoutFrame } from 'hooks/useWithoutFrame'
import { formatLocalTimeDateString } from 'utils/timezone'

import { AllocineProviderParameters } from './AllocineProviderParameters'
import { CinemaProviderParameters } from './CinemaProviderParameters'
import { DeleteVenueProviderButton } from './DeleteVenueProviderButton'
import { ToggleVenueProviderStatusButton } from './ToggleVenueProviderStatusButton'
import style from './VenueProviderItem.module.scss'

interface VenueProviderItemV2Props {
  venueProvider: VenueProviderResponse
  venue: GetVenueResponseModel
  venueDepartmentCode?: string | null
  offererId: number
}

export const VenueProviderItem = ({
  venueProvider,
  venue,
  venueDepartmentCode,
  offererId,
}: VenueProviderItemV2Props): JSX.Element => {
  const { lastSyncDate, provider, venueIdAtOfferProvider } = venueProvider

  const providerInfo = getProviderInfo(provider.name)
  const isWithoutFrame = useWithoutFrame()

  return (
    <li
      className={cn(style['venue-provider-row'], {
        [style['venue-provider-row-without-frame']]: isWithoutFrame,
      })}
    >
      <div
        className={cn(style['venue-provider-item-info'], {
          [style['venue-provider-item-info-without-frame']]: isWithoutFrame,
        })}
      >
        <div className={style['provider-name-container']}>
          <div className={style['provider-name']}>
            {providerInfo?.name ?? provider.name}
          </div>

          <div className={style['provider-actions']}>
            <ToggleVenueProviderStatusButton
              venueProvider={venueProvider}
              venue={venue}
            />

            <DeleteVenueProviderButton
              venueProviderId={venueProvider.id}
              venue={venue}
            />
          </div>
        </div>

        {!venueProvider.provider.hasOffererProvider ? (
          !lastSyncDate ? (
            <div className={style['venue-id-at-offer-provider-container']}>
              <div>
                Compte : <span>{venueIdAtOfferProvider}</span>
              </div>

              <span className={style['venue-id-at-offer-provider-message']}>
                Importation en cours. Cette étape peut durer plusieurs dizaines
                de minutes. Vous pouvez fermer votre navigateur et revenir plus
                tard.
              </span>
            </div>
          ) : (
            <div className={style['venue-id-at-offer-provider-container']}>
              <div className={style['last-synchronisation']}>
                <span>Dernière synchronisation :</span>

                <span>
                  &nbsp;
                  {formatLocalTimeDateString(
                    lastSyncDate,
                    venueDepartmentCode,
                    'dd/MM/yyyy à HH:mm'
                  )}
                </span>
              </div>

              <div>
                Compte : <span>{venueIdAtOfferProvider}</span>
              </div>
            </div>
          )
        ) : null}
      </div>

      {isAllocineProvider(venueProvider.provider) && (
        <AllocineProviderParameters
          venueProvider={venueProvider}
          venue={venue}
          offererId={offererId}
        />
      )}

      {isCinemaProvider(venueProvider.provider) && (
        <CinemaProviderParameters
          venueProvider={venueProvider}
          venue={venue}
          offererId={offererId}
        />
      )}
    </li>
  )
}
