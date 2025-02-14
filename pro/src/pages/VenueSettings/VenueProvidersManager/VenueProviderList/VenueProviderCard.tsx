import { GetVenueResponseModel, VenueProviderResponse } from 'apiClient/v1'
import { getProviderInfo } from 'commons/core/Providers/utils/getProviderInfo'
import {
  isAllocineProvider,
  isCinemaProvider,
} from 'commons/core/Providers/utils/utils'
import { formatLocalTimeDateString } from 'commons/utils/timezone'

import { AllocineProviderEdit } from './AllocineProviderEdit'
import { CinemaProviderEdit } from './CinemaProviderEdit'
import { DeleteVenueProviderButton } from './DeleteVenueProviderButton'
import { ToggleVenueProviderStatusButton } from './ToggleVenueProviderStatusButton'
import style from './VenueProviderCard.module.scss'

export interface VenueProviderCardProps {
  venueProvider: VenueProviderResponse
  venue: GetVenueResponseModel
  venueDepartmentCode?: string | null
  offererId: number
}

export const VenueProviderCard = ({
  venueProvider,
  venue,
  venueDepartmentCode,
  offererId,
}: VenueProviderCardProps): JSX.Element => {
  const { lastSyncDate, provider, venueIdAtOfferProvider, dateCreated } =
    venueProvider

  const providerInfo = getProviderInfo(provider.name)

  const isPublicAPIProvider = venueProvider.provider.hasOffererProvider

  return (
    <div className={style['venue-provider-card']}>
      <div className={style['provider-info-container']}>
        {providerInfo && providerInfo.logo && (
          <img
            alt={providerInfo.name}
            src={providerInfo.logo}
            className={style['provider-logo']}
          />
        )}
        <div className={style['provider-name']}>
          {providerInfo?.name ?? provider.name}
        </div>
      </div>
      {isPublicAPIProvider ? (
        <div className={style['venue-provider-info-container']}>
          <div className={style['venue-provider-account-info']}>
            Date d&apos;ajout :
            <span>
              &nbsp;
              {formatLocalTimeDateString(
                dateCreated,
                venueDepartmentCode,
                'dd/MM/yyyy à HH:mm'
              )}
            </span>
          </div>
        </div>
      ) : (
        <div className={style['venue-provider-info-container']}>
          <div className={style['venue-provider-account-info']}>
            Compte : <span>{venueIdAtOfferProvider}</span>
          </div>
          {lastSyncDate ? (
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
          ) : (
            <div>
              Importation en cours. Cette étape peut durer plusieurs dizaines de
              minutes.
            </div>
          )}
        </div>
      )}
      <div className={style['provider-actions-container']}>
        {isAllocineProvider(venueProvider.provider) && (
          <AllocineProviderEdit
            venueProvider={venueProvider}
            venue={venue}
            offererId={offererId}
          />
        )}

        {isCinemaProvider(venueProvider.provider) && (
          <CinemaProviderEdit
            venueProvider={venueProvider}
            venue={venue}
            offererId={offererId}
          />
        )}
        <div className={style['provider-actions-delete-and-inactivate']}>
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
    </div>
  )
}
