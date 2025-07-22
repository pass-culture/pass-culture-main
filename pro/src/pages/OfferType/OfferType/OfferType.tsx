import { FormProvider, useForm } from 'react-hook-form'
import { useSelector } from 'react-redux'
import { useLocation, useNavigate } from 'react-router'

import { api } from 'apiClient/api'
import { CollectiveOfferType as CollectiveOfferApiType } from 'apiClient/v1'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  INDIVIDUAL_OFFER_SUBTYPE,
  OFFER_TYPES,
  OFFER_WIZARD_MODE,
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { serializeApiCollectiveFilters } from 'commons/core/Offers/utils/serializer'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RadioButtonGroup } from 'design-system/RadioButtonGroup/RadioButtonGroup'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ActionsBar } from './ActionsBar/ActionsBar'
import { CollectiveOfferType } from './CollectiveOfferType/CollectiveOfferType'
import { IndividualOfferType } from './IndividualOfferType/IndividualOfferType'
import styles from './OfferType.module.scss'
import { OfferTypeFormValues } from './types'

export const OfferTypeScreen = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = useSelector(selectCurrentOffererId)?.toString()
  const queryVenueId = queryParams.get('lieu')
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  const notify = useNotification()

  const initialValues: OfferTypeFormValues = {
    offer: {
      offerType: OFFER_TYPES.INDIVIDUAL_OR_DUO,
      collectiveOfferSubtype: COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE,
      collectiveOfferSubtypeDuplicate:
        COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER,
      individualOfferSubtype: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
    },
  }

  const methods = useForm<OfferTypeFormValues>({
    defaultValues: initialValues,
  })

  const { handleSubmit, setValue, getValues, watch } = methods

  const offer = watch('offer')

  const { data: offerer, isLoading: isOffererLoading } =
    useOfferer(queryOffererId)

  const isOnboarding = location.pathname.indexOf('onboarding') !== -1

  const onSubmit = async ({ offer }: OfferTypeFormValues) => {
    if (offer.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO) {
      const params = new URLSearchParams(location.search)
      if (!isNewOfferCreationFlowFeatureActive) {
        params.append('offer-type', offer.individualOfferSubtype)
      }

      return navigate({
        pathname: getIndividualOfferUrl({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isOnboarding,
        }),
        search: params.toString(),
      })
    }

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
        ...DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
        offererId: queryOffererId ? queryOffererId : 'all',
        venueId: queryVenueId ? queryVenueId : 'all',
      }
      const {
        nameOrIsbn,
        offererId,
        venueId,
        status,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        format,
      } = serializeApiCollectiveFilters(
        apiFilters,
        DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS
      )

      const templateOffersOnSelectedVenue = await api.getCollectiveOffers(
        nameOrIsbn,
        offererId,
        status,
        venueId,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        CollectiveOfferApiType.TEMPLATE,
        format
      )

      if (templateOffersOnSelectedVenue.length === 0) {
        return notify.error(
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

  const isDisabledForEducationnal =
    offer.offerType === OFFER_TYPES.EDUCATIONAL && !offerer?.allowedOnAdage

  return (
    <>
      <div className={styles['offer-type-container']}>
        <FormProvider {...methods}>
          <form onSubmit={handleSubmit(onSubmit)}>
            <FormLayout>
              {/* If we're on boarding process, we don't need to ask for offer type (we already chose individual at previous step) */}
              {!isOnboarding && (
                <RadioButtonGroup
                  variant="detailed"
                  name="offerType"
                  label="À qui destinez-vous cette offre ?"
                  labelTag="h2"
                  onChange={(e) =>
                    setValue('offer.offerType', e.target.value as OFFER_TYPES)
                  }
                  checkedOption={getValues('offer.offerType')}
                  options={[
                    {
                      label: 'Au grand public',
                      value: OFFER_TYPES.INDIVIDUAL_OR_DUO,
                    },
                    {
                      label: 'À un groupe scolaire',
                      value: OFFER_TYPES.EDUCATIONAL,
                    },
                  ]}
                  display="horizontal"
                />
              )}

              {!isNewOfferCreationFlowFeatureActive &&
                offer.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO && (
                  <IndividualOfferType />
                )}

              {offer.offerType === OFFER_TYPES.EDUCATIONAL &&
                (isOffererLoading ? (
                  <Spinner />
                ) : (
                  <CollectiveOfferType offerer={offerer} />
                ))}

              <ActionsBar disableNextButton={isDisabledForEducationnal} />
            </FormLayout>
          </form>
        </FormProvider>
      </div>
    </>
  )
}
