import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializeApiCollectiveFilters'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import {
  ensureCurrentOfferer,
  selectCurrentOfferer,
} from '@/commons/store/offerer/selectors'
import { ensureSelectedVenue } from '@/commons/store/user/selectors'
import { CollectiveBudgetBanner } from '@/components/CollectiveBudgetInformation/CollectiveBudgetBanner'
import { FormLayout } from '@/components/FormLayout/FormLayout'

import { ActionsBar } from '../ActionsBar/ActionsBar'
import { CollectiveOfferType } from '../CollectiveOfferType/CollectiveOfferType'
import styles from './OfferType.module.scss'
import type { OfferTypeFormValues } from './types'

export const OfferTypeScreen = () => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const navigate = useNavigate()
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const selectedOffererId = useAppSelector(ensureCurrentOfferer).id
  const selectedVenue = useAppSelector(ensureSelectedVenue)
  const queryVenueId = queryParams.get('lieu')

  const snackBar = useSnackBar()

  const methods = useForm<OfferTypeFormValues>({
    defaultValues: {
      offer: {
        collectiveOfferSubtype: COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE,
        collectiveOfferSubtypeDuplicate:
          COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER,
      },
    },
  })

  const { handleSubmit } = methods

  const offerer = useAppSelector(selectCurrentOfferer)

  const onSubmit = async ({ offer }: OfferTypeFormValues) => {
    if (offer.collectiveOfferSubtype === COLLECTIVE_OFFER_SUBTYPE.TEMPLATE) {
      return navigate({
        pathname: '/offre/creation/collectif/vitrine',
        search: location.search,
      })
    }

    if (
      offer.collectiveOfferSubtypeDuplicate ===
      COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE
    ) {
      const apiFilters = {
        ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
        offererId: selectedOffererId.toString(),
        venueId: withSwitchVenueFeature
          ? selectedVenue.id.toString()
          : (queryVenueId ?? undefined),
      }
      const {
        name,
        offererId,
        venueId,
        status,
        periodBeginningDate,
        periodEndingDate,
        format,
        locationType,
        offererAddressId,
      } = serializeApiCollectiveFilters(apiFilters)

      const templateOffersOnSelectedVenue =
        await api.getCollectiveOfferTemplates(
          name,
          offererId,
          status,
          venueId,
          periodBeginningDate,
          periodEndingDate,
          format,
          locationType,
          offererAddressId
        )

      if (templateOffersOnSelectedVenue.length === 0) {
        return snackBar.error(
          'Vous devez créer une offre vitrine avant de pouvoir utiliser cette fonctionnalité'
        )
      } else {
        return navigate({
          pathname: '/offre/creation/collectif/selection',
          search: location.search,
        })
      }
    }

    return navigate({
      pathname: '/offre/creation/collectif',
      search: location.search,
    })
  }

  return (
    <>
      <CollectiveBudgetBanner />
      <div className={styles['offer-type-container']}>
        <FormProvider {...methods}>
          <form onSubmit={handleSubmit(onSubmit)}>
            <FormLayout>
              <CollectiveOfferType offerer={offerer} />

              <ActionsBar disableNextButton={!offerer?.allowedOnAdage} />
            </FormLayout>
          </form>
        </FormProvider>
      </div>
    </>
  )
}
