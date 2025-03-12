import { FormikProvider, useFormik } from 'formik'
import { useSelector } from 'react-redux'
import { useLocation, useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveOfferType as CollectiveOfferApiType,
  GetOfferersNamesResponseModel,
} from 'apiClient/v1'
import { GET_OFFERER_NAMES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  INDIVIDUAL_OFFER_SUBTYPE,
  OFFER_TYPES,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { serializeApiCollectiveFilters } from 'commons/core/Offers/utils/serializer'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { CollectiveBudgetCallout } from 'components/CollectiveBudgetInformation/CollectiveBudgetCallout'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import phoneStrokeIcon from 'icons/stroke-phone.svg'
import strokeProfIcon from 'icons/stroke-prof.svg'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ActionsBar } from './ActionsBar/ActionsBar'
import { CollectiveOfferType } from './CollectiveOfferType/CollectiveOfferType'
import { IndividualOfferType } from './IndividualOfferType/IndividualOfferType'
import styles from './OfferType.module.scss'
import { OfferTypeFormValues } from './types'

export const OfferTypeScreen = (): JSX.Element => {
  const navigate = useNavigate()
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = useSelector(selectCurrentOffererId)?.toString()
  const queryVenueId = queryParams.get('lieu')

  const notify = useNotification()
  const initialValues: OfferTypeFormValues = {
    offerType: OFFER_TYPES.INDIVIDUAL_OR_DUO,
    collectiveOfferSubtype: COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE,
    collectiveOfferSubtypeDuplicate:
      COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER,
    individualOfferSubtype: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
  }

  const { data } = useSWR<
    GetOfferersNamesResponseModel | null,
    string,
    [string]
  >([GET_OFFERER_NAMES_QUERY_KEY], () => api.listOfferersNames())
  const offerersNames = data?.offerersNames

  //  If there is no offerer id in the url, consider the first offerer found in the user's offerers list
  const offererId = queryOffererId || offerersNames?.[0].id
  const { data: offerer, isLoading: isOffererLoading } = useOfferer(offererId)

  const isOnboarding = location.pathname.indexOf('onboarding') !== -1
  const onSubmit = async (values: OfferTypeFormValues) => {
    if (values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO) {
      const params = new URLSearchParams(location.search)
      if (values.individualOfferSubtype) {
        params.append('offer-type', values.individualOfferSubtype)
      }

      return navigate({
        pathname: getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isOnboarding,
        }),
        search: params.toString(),
      })
    }

    // Offer type is EDUCATIONAL
    if (values.collectiveOfferSubtype === COLLECTIVE_OFFER_SUBTYPE.TEMPLATE) {
      return navigate({
        pathname: '/offre/creation/collectif/vitrine',
        search: location.search,
      })
    }
    if (
      values.collectiveOfferSubtypeDuplicate ===
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
        categoryId,
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
        categoryId,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        CollectiveOfferApiType.TEMPLATE,
        format
      )

      if (templateOffersOnSelectedVenue.length === 0) {
        notify.error(
          'Vous devez créer une offre vitrine avant de pouvoir utiliser cette fonctionnalité'
        )
        return
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

  const formik = useFormik<OfferTypeFormValues>({
    initialValues: initialValues,
    onSubmit,
  })
  const { values } = formik

  const isDisabledForEducationnal =
    values.offerType === OFFER_TYPES.EDUCATIONAL && !offerer?.allowedOnAdage

  const hasNotChosenOfferType = values.individualOfferSubtype === ''

  const isDisableForIndividual =
    values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO && hasNotChosenOfferType

  return (
    <>
      {!isOnboarding && offerer?.allowedOnAdage && (
        <CollectiveBudgetCallout pageName="offer-creation-hub" />
      )}
      <div className={styles['offer-type-container']}>
        <h1 className={styles['offer-type-title']}>Créer une offre</h1>
        <FormikProvider value={formik}>
          <form onSubmit={formik.handleSubmit}>
            <FormLayout>
              {/* If we're on boarding process, we don't need to ask for offer type (we already chose individual at previous step) */}
              {!isOnboarding && (
                <RadioGroup
                  name="offerType"
                  legend={
                    <h2 className={styles['legend']}>
                      À qui destinez-vous cette offre ?
                    </h2>
                  }
                  group={[
                    {
                      label: 'Au grand public',
                      value: OFFER_TYPES.INDIVIDUAL_OR_DUO,
                      icon: phoneStrokeIcon,
                      iconPosition: 'center',
                    },
                    {
                      label: 'À un groupe scolaire',
                      value: OFFER_TYPES.EDUCATIONAL,
                      icon: strokeProfIcon,
                      iconPosition: 'center',
                    },
                  ]}
                  variant={RadioVariant.BOX}
                  displayMode="inline-grow"
                />
              )}
              {values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO && (
                <IndividualOfferType />
              )}
              {values.offerType === OFFER_TYPES.EDUCATIONAL &&
                (isOffererLoading ? (
                  <Spinner />
                ) : (
                  <CollectiveOfferType offerer={offerer} />
                ))}
              <ActionsBar
                disableNextButton={
                  isDisabledForEducationnal || isDisableForIndividual
                }
              />
            </FormLayout>
          </form>
        </FormikProvider>
      </div>
    </>
  )
}
