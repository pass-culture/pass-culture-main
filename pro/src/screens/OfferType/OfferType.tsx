import { FormikProvider, useFormik } from 'formik'
import { useSelector } from 'react-redux'
import { useLocation, useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { CollectiveOfferType as CollectiveOfferApiType } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { GET_OFFERER_QUERY_KEY } from 'config/swrQueryKeys'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  OFFER_TYPES,
  OFFER_WIZARD_MODE,
} from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { serializeApiCollectiveFilters } from 'core/Offers/utils/serializer'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { useNotification } from 'hooks/useNotification'
import { useSuggestedSubcategoriesAbTest } from 'hooks/useSuggestedSubcategoriesAbTest'
import phoneStrokeIcon from 'icons/stroke-phone.svg'
import strokeProfIcon from 'icons/stroke-prof.svg'
import { selectCurrentOffererId } from 'store/user/selectors'
import { RadioButtonWithImage } from 'ui-kit/RadioButtonWithImage/RadioButtonWithImage'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ActionsBar } from './ActionsBar/ActionsBar'
import { CollectiveOfferType } from './CollectiveOfferType/CollectiveOfferType'
import { IndividualOfferType } from './IndividualOfferType/IndividualOfferType'
import styles from './OfferType.module.scss'
import { OfferTypeFormValues } from './types'

export const OfferTypeScreen = (): JSX.Element => {
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const isSplitOfferEnabled = useActiveFeature('WIP_SPLIT_OFFER')
  const navigate = useNavigate()
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const queryOffererId = isNewInterfaceActive
    ? selectedOffererId?.toString()
    : queryParams.get('structure')
  const queryVenueId = queryParams.get('lieu')

  const notify = useNotification()
  const initialValues: OfferTypeFormValues = {
    offerType: OFFER_TYPES.INDIVIDUAL_OR_DUO,
    collectiveOfferSubtype: COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE,
    collectiveOfferSubtypeDuplicate:
      COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER,
    individualOfferSubtype: '',
  }

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, queryOffererId],
    async function ([, offererIdParam]) {
      if (!offererIdParam) {
        //  If there is no offerer id in the url, consider the first offerer found in the user's offerers list
        const offerers = await api.listOfferersNames()
        if (offerers.offerersNames.length === 0) {
          return
        }
        const firstoffererId = offerers.offerersNames[0].id
        return api.getOfferer(firstoffererId)
      }
      return api.getOfferer(Number(offererIdParam))
    }
  )

  const offerer = offererQuery.data

  const areSuggestedSubcategoriesUsed = useSuggestedSubcategoriesAbTest(
    offerer?.managedVenues ?? []
  )

  const onSubmit = async (values: OfferTypeFormValues) => {
    if (values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO) {
      const params = new URLSearchParams(location.search)
      if (values.individualOfferSubtype) {
        params.append('offer-type', values.individualOfferSubtype)
      }

      return isSplitOfferEnabled
        ? navigate({
            pathname: getIndividualOfferUrl({
              step: OFFER_WIZARD_STEP_IDS.DETAILS,
              mode: OFFER_WIZARD_MODE.CREATION,
              isSplitOfferEnabled,
            }),
            search: params.toString(),
          })
        : navigate({
            pathname: getIndividualOfferUrl({
              step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
              mode: OFFER_WIZARD_MODE.CREATION,
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
  const { values, handleChange } = formik

  const isDisabledForEducationnal =
    values.offerType === OFFER_TYPES.EDUCATIONAL && !offerer?.allowedOnAdage

  const hasNotChosenOfferType = values.individualOfferSubtype === ''

  const isDisableForIndividual =
    values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO &&
    hasNotChosenOfferType &&
    !areSuggestedSubcategoriesUsed

  return (
    <div className={styles['offer-type-container']}>
      <h1 className={styles['offer-type-title']}>Créer une offre</h1>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <FormLayout>
            <FormLayout.Section title="À qui destinez-vous cette offre ?">
              <FormLayout.Row inline>
                <RadioButtonWithImage
                  name="offerType"
                  icon={phoneStrokeIcon}
                  isChecked={values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO}
                  label="Au grand public"
                  onChange={handleChange}
                  value={OFFER_TYPES.INDIVIDUAL_OR_DUO}
                  className={styles['offer-type-button']}
                />
                <RadioButtonWithImage
                  name="offerType"
                  icon={strokeProfIcon}
                  isChecked={values.offerType === OFFER_TYPES.EDUCATIONAL}
                  label="À un groupe scolaire"
                  onChange={handleChange}
                  value={OFFER_TYPES.EDUCATIONAL}
                  className={styles['offer-type-button']}
                />
              </FormLayout.Row>
            </FormLayout.Section>

            {!areSuggestedSubcategoriesUsed &&
              values.offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO && (
                <IndividualOfferType />
              )}

            {values.offerType === OFFER_TYPES.EDUCATIONAL &&
              (offererQuery.isLoading ? (
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
  )
}
