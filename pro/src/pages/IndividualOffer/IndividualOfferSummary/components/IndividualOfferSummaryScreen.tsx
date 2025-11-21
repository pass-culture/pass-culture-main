import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate, useSearchParams } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { getHumanReadableApiError } from '@/apiClient/helpers'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useNotification } from '@/commons/hooks/useNotification'
import { selectCurrentOfferer } from '@/commons/store/offerer/selectors'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { getOffererData } from '@/commons/utils/offererStoreHelper'
import { serializeDateTimeToUTCFromLocalDepartment } from '@/commons/utils/timezone'
import { DisplayOfferInAppLink } from '@/components/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { OfferAppPreview } from '@/components/OfferAppPreview/OfferAppPreview'
import { RedirectToBankAccountDialog } from '@/components/RedirectToBankAccountDialog/RedirectToBankAccountDialog'
import { SummaryAside } from '@/components/SummaryLayout/SummaryAside'
import { SummaryContent } from '@/components/SummaryLayout/SummaryContent'
import { SummaryLayout } from '@/components/SummaryLayout/SummaryLayout'
import { Banner } from '@/design-system/Banner/Banner'
import phoneStrokeIcon from '@/icons/stroke-phone.svg'
import { getOfferConditionalFields } from '@/pages/IndividualOffer/commons/getOfferConditionalFields'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import { MediaSection } from '@/pages/IndividualOfferSummary/components/MediaSection/MediaSection'
import { PriceCategoriesSection } from '@/pages/IndividualOfferSummary/components/PriceCategoriesSection/PriceCategoriesSection'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { EventPublicationForm } from './EventPublicationForm/EventPublicationForm'
import type { EventPublicationFormValues } from './EventPublicationForm/types'
import { validationSchema } from './EventPublicationForm/validationSchema'
import styles from './IndividualOfferSummaryScreen.module.scss'
import { OfferSection } from './OfferSection/OfferSection'
import { StockSection } from './StockSection/StockSection'

interface IndividualOfferSummaryScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
}
export const IndividualOfferSummaryScreen = ({
  offer,
}: Readonly<IndividualOfferSummaryScreenProps>) => {
  const [displayRedirectDialog, setDisplayRedirectDialog] = useState(false)
  const notification = useNotification()
  const { mutate } = useSWRConfig()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const { subCategories, hasPublishedOfferWithSameEan } =
    useIndividualOfferContext()
  const [searchParams, setSearchParams] = useSearchParams()
  const currentOfferer = useAppSelector(selectCurrentOfferer)

  const onPublish = async (values: EventPublicationFormValues) => {
    const departmentCode = getDepartmentCode(offer)

    try {
      const offererId = offer.venue.managingOfferer.id
      const offererResponse = await getOffererData(
        offererId,
        currentOfferer,
        () => api.getOfferer(offererId)
      )
      const publishIndividualOfferResponse = await api.patchPublishOffer({
        id: offer.id,
        publicationDatetime:
          values.publicationMode === 'later' &&
          values.publicationDate &&
          values.publicationTime
            ? serializeDateTimeToUTCFromLocalDepartment(
                values.publicationDate,
                values.publicationTime,
                departmentCode
              )
            : undefined,
        bookingAllowedDatetime:
          values.bookingAllowedMode === 'later' &&
          values.bookingAllowedDate &&
          values.bookingAllowedTime
            ? serializeDateTimeToUTCFromLocalDepartment(
                values.bookingAllowedDate,
                values.bookingAllowedTime,
                departmentCode
              )
            : undefined,
      })
      await mutate([GET_OFFER_QUERY_KEY, offer.id])

      const shouldDisplayRedirectDialog =
        isOnboarding ||
        (publishIndividualOfferResponse.isNonFreeOffer &&
          !offererResponse?.hasNonFreeOffer &&
          !offererResponse?.hasValidBankAccount &&
          !offererResponse?.hasPendingBankAccount)

      if (shouldDisplayRedirectDialog) {
        setSearchParams(
          { ...searchParams, userHasJustOnBoarded: '1' },
          { replace: true }
        )
        setDisplayRedirectDialog(true)
      } else {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        navigate(offerConfirmationStepUrl)
      }
    } catch (error) {
      notification.error(getHumanReadableApiError(error))
    }
  }
  const methods = useForm<EventPublicationFormValues>({
    defaultValues: {
      publicationMode: 'now',
      publicationDate: '',
      publicationTime: '',
      bookingAllowedMode: 'now',
      bookingAllowedDate: '',
      bookingAllowedTime: '',
    },
    resolver: yupResolver(validationSchema),
  })

  if (offer === null) {
    return null
  }

  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const offerConfirmationStepUrl = isOnboarding
    ? '/accueil'
    : getIndividualOfferUrl({
        offerId: offer.id,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        mode: OFFER_WIZARD_MODE.CREATION,
        isOnboarding,
      })

  /* istanbul ignore next: DEBT, TO FIX */
  const handlePreviousStep = () => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
        mode: OFFER_WIZARD_MODE.CREATION,
        isOnboarding,
      })
    )
  }
  const offerSubCategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )
  assertOrFrontendError(
    offerSubCategory,
    `'offerSubCategory' with id "${offer.subcategoryId}" not found in subCategories.`
  )

  const offerConditionalFields = getOfferConditionalFields({
    offerSubcategory: offerSubCategory,
    shouldReceiveEmailNotifications: true,
  })
  const conditionalFields = [
    ...offerSubCategory.conditionalFields,
    ...offerConditionalFields,
  ]

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onPublish)}>
        <div className={styles['offer-preview-banners']}>
          <Banner
            title="Vous y êtes presque !"
            description="Vérifiez les informations ci-dessous avant de publier votre offre."
          />

          <EventPublicationForm />
        </div>

        <SummaryLayout>
          <SummaryContent>
            <OfferSection conditionalFields={conditionalFields} offer={offer} />
            <MediaSection
              offerId={offer.id}
              videoData={offer.videoData}
              isOnCreation
            />
            {offer.isEvent && (
              <PriceCategoriesSection
                offer={offer}
                canBeDuo={canBeDuo}
                shouldShowDivider
              />
            )}
            <StockSection offer={offer} canBeDuo={canBeDuo} />
          </SummaryContent>

          <SummaryAside>
            <div className={styles['offer-creation-preview-title']}>
              <SvgIcon
                src={phoneStrokeIcon}
                alt=""
                className={styles['icon-info-phone']}
              />
              <h2 className={styles.title}>Aperçu dans l’app</h2>
            </div>

            <OfferAppPreview offer={offer} />

            <div className={styles['offer-preview-app-link']}>
              <DisplayOfferInAppLink
                id={offer.id}
                variant={ButtonVariant.SECONDARY}
              >
                Visualiser dans l’app
              </DisplayOfferInAppLink>
            </div>
          </SummaryAside>
        </SummaryLayout>

        <ActionBar
          onClickPrevious={handlePreviousStep}
          step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY}
          publicationMode={methods.watch('publicationMode')}
          isDisabled={
            methods.formState.isSubmitting || hasPublishedOfferWithSameEan
          }
        />

        <RedirectToBankAccountDialog
          cancelRedirectUrl={offerConfirmationStepUrl}
          offerId={offer.venue.managingOfferer.id}
          venueId={offer.venue.id}
          isDialogOpen={displayRedirectDialog}
        />
      </form>
    </FormProvider>
  )
}
