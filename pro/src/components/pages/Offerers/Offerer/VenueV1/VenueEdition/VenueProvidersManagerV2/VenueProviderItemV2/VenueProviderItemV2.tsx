import React from 'react'

import { getProviderInfo } from 'components/pages/Offers/domain/getProviderInfo'
import { isAllocineProvider, isCinemaProvider } from 'core/Providers'
import { pluralize } from 'utils/pluralize'
import { formatLocalTimeDateString } from 'utils/timezone'

import { IVenueProviderApi } from '../../VenueProvidersManager/CinemaProviderItem/types'
import AllocineProviderParameters from '../AllocineProviderParamaters/AllocineProviderParameters'
import CinemaProviderParameters from '../CinemaProviderParameters/CinemaProviderParameters'
import DeleteVenueProviderButton from '../DeleteVenueProviderButton/DeleteVenueProviderButton'
import ToggleVenueProviderStatusButton from '../ToggleVenueProviderStatusButton/ToggleVenueProviderStatusButton'

import style from './VenueProviderItemV2.module.scss'

export interface IVenueProviderItemV2Props {
  afterDelete: (deletedVenueProvider: string) => void
  afterSubmit: (editedVenueProvider: IVenueProviderApi) => void
  venueProvider: IVenueProviderApi
  venueDepartmentCode: string
}

const VenueProviderItemV2 = ({
  afterDelete,
  afterSubmit,
  venueProvider,
  venueDepartmentCode,
}: IVenueProviderItemV2Props): JSX.Element => {
  const { lastSyncDate, nOffers, provider, venueIdAtOfferProvider } =
    venueProvider

  const providerInfo = getProviderInfo(provider.name)

  return (
    <li className={style['venue-provider-row']}>
      <div className={style['venue-provider-item-info']}>
        <div className={style['provider-name-container']}>
          <div className={style['provider-name']}>
            {providerInfo?.name ?? provider.name}
          </div>
          <div className={style['provider-actions']}>
            <ToggleVenueProviderStatusButton
              venueProvider={venueProvider}
              afterEdit={afterSubmit}
            />
            <DeleteVenueProviderButton
              afterDelete={afterDelete}
              venueProviderId={venueProvider.id}
            />
          </div>
        </div>
        {!lastSyncDate ? (
          <div className={style['venue-id-at-offer-provider-container']}>
            <div className="venue-id-at-offer-provider">
              Compte : <span>{venueIdAtOfferProvider}</span>
            </div>
            <span>
              Importation en cours. Cette étape peut durer plusieurs dizaines de
              minutes. Vous pouvez fermer votre navigateur et revenir plus tard.
            </span>
          </div>
        ) : (
          <div className={style['venue-id-at-offer-provider-container']}>
            <div className={style['last-synchronisation']}>
              <span>Dernière synchronisation :</span>
              <span data-testId="last-sync-date">
                &nbsp;
                {formatLocalTimeDateString(
                  lastSyncDate,
                  venueDepartmentCode,
                  'dd/MM/yyyy à HH:mm'
                )}
              </span>
            </div>
            <div className="venue-id-at-offer-provider">
              Compte : <span>{venueIdAtOfferProvider}</span>
            </div>
            <div className="offers-container-counter">
              Offres synchronisées : <span>{pluralize(nOffers, 'offres')}</span>
            </div>
          </div>
        )}
      </div>
      {isAllocineProvider(venueProvider.provider) && (
        <AllocineProviderParameters
          venueProvider={venueProvider}
          afterVenueProviderEdit={afterSubmit}
        />
      )}
      {isCinemaProvider(venueProvider.provider) && (
        <CinemaProviderParameters
          venueProvider={venueProvider}
          afterVenueProviderEdit={afterSubmit}
        />
      )}
    </li>
  )
}

export default VenueProviderItemV2
