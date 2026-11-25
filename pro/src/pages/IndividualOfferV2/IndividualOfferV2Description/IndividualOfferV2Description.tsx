import { zodResolver } from '@hookform/resolvers/zod'
import { useRef } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { Navigate, useLocation, useNavigate } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { getHumanReadableApiError, isErrorAPIError } from '@/apiClient/helpers'
import { FieldEnum } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_CAPABILITIES_QUERY_KEY,
  GET_OFFER_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferImage } from '@/commons/core/Offers/utils/getIndividualOfferImage'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import {
  HasCapability,
  OfferCapabilityProvider,
} from '@/commons/core/Offers/utils/offerCapabilityContext/offerCapabilityContext'
import { isOfferProductBasedButNotSynchronized } from '@/commons/core/Offers/utils/typology'
import { PATCH_SUCCESS_MESSAGE } from '@/commons/core/shared/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import {
  CheckboxGroup,
  type CheckboxGroupOption,
} from '@/design-system/CheckboxGroup/CheckboxGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import strokeAccessibilityEyeIcon from '@/icons/stroke-accessibility-eye.svg'
import strokeLeftIcon from '@/icons/stroke-left.svg'
import strokeRightIcon from '@/icons/stroke-right.svg'
import { useIndividualOfferImageUpload } from '@/pages/IndividualOffer/commons/useIndividualOfferImageUpload'
import { getAfterSubmitPath } from '@/pages/IndividualOffer/commons/utils/getAfterSubmitPath'
import { DEFAULT_DESCRIPTION_FORM_VALUES } from '@/pages/IndividualOfferV2/IndividualOfferV2Description/constants'
import {
  getFormV2ReadOnlyFields,
  getInitialValuesFromOfferV2,
} from '@/pages/IndividualOfferV2/IndividualOfferV2Description/utilsV2'
import {
  type DescriptionFormInputValues,
  type DescriptionFormValues,
  getValidationSchema,
} from '@/pages/IndividualOfferV2/IndividualOfferV2Description/validationSchemaV2'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferV2DescriptionExtraData } from './IndividualOfferV2DescriptionExtraData/IndividualOfferV2DescriptionExtraData'
import { IndividualOfferV2DescriptionImage } from './IndividualOfferV2DescriptionImage/IndividualOfferV2DescriptionImage'
import {
  serializeDescriptionPatchData,
  serializeDescriptionPostData,
} from './serializers'

const IndividualOfferV2Description = (): JSX.Element => {
  const { offer } = useIndividualOfferContext()
  const offerIdRef = useRef(offer?.id)
  const mode = useOfferWizardMode()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const nfd = useAppSelector((state) => state.nfd)
  const { nature, format } = offer ?? nfd
  const isNewDraftOffer = !offer
  const hasSavedOfferRef = useRef(false)
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()
  const { mutate } = useSWRConfig()
  const snackBar = useSnackBar()

  assertOrFrontendError(nature, '`nature` is missing.')
  assertOrFrontendError(format, '`format` is missing.')

  const {
    displayedImage,
    hasUpsertedImage,
    onImageUpload,
    onImageDelete,
    handleImageOnSubmit,
  } = useIndividualOfferImageUpload(getIndividualOfferImage(offer))
  const isImageReadOnly =
    withVenueHelpers(selectedPartnerVenue).isClosed ||
    (!!offer && isOfferProductBasedButNotSynchronized(offer))

  const hasOfferCapabilities =
    !!offer?.nature && !!offer.format && offer.capabilities.length > 0

  const { data, isLoading } = useSWR(
    !hasOfferCapabilities && nature && format
      ? [GET_CAPABILITIES_QUERY_KEY, nature, format]
      : null,
    ([, natureParam, formatParam]) =>
      api.getCapabilities({
        query: { nature: natureParam, format: formatParam },
      })
  )
  const capabilities = hasOfferCapabilities
    ? offer.capabilities
    : (data?.capabilities ?? [])
  const mandatoryFields = hasOfferCapabilities
    ? offer.mandatoryFields
    : (data?.mandatoryFields ?? [])

  const form = useForm<
    DescriptionFormInputValues,
    unknown,
    DescriptionFormValues
  >({
    defaultValues: isNewDraftOffer
      ? DEFAULT_DESCRIPTION_FORM_VALUES
      : getInitialValuesFromOfferV2(offer),
    resolver: zodResolver(getValidationSchema(mandatoryFields)),
    mode: 'onBlur',
  })

  const isLargePrint = !!form.watch('visualDisabilityCompliant')

  const accessibilityOptions: CheckboxGroupOption[] = [
    {
      label: 'Livre en gros caractères',
      asset: { variant: 'icon', src: strokeAccessibilityEyeIcon },
      sizing: 'fill',
      checked: isLargePrint,
      onChange: (event: React.ChangeEvent<HTMLInputElement>) =>
        form.setValue('visualDisabilityCompliant', event.target.checked, {
          shouldDirty: true,
          shouldValidate: true,
        }),
    },
  ]

  const onSubmit = async (
    formValues: DescriptionFormValues
  ): Promise<boolean> => {
    try {
      if (offerIdRef.current) {
        await mutate(
          [GET_OFFER_QUERY_KEY, offerIdRef.current],
          api.patchOffer({
            path: { offer_id: offerIdRef.current },
            body: serializeDescriptionPatchData(formValues, readOnlyFields),
          }),
          { revalidate: false }
        )
      } else {
        await mutate(
          [GET_OFFER_QUERY_KEY],
          api.createOffer({
            body: serializeDescriptionPostData(
              formValues,
              selectedPartnerVenue.id,
              nature,
              format
            ),
          }),
          {
            revalidate: false,
            populateCache: (newOffer) => {
              offerIdRef.current = newOffer.id
              return newOffer
            },
          }
        )

        // Replace current history entry so that it points to this new offer ID when clicking the browser back button
        globalThis.history.replaceState(
          globalThis.history.state,
          '',
          getIndividualOfferUrl({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION_V2,
            offerId: offerIdRef.current,
            mode: OFFER_WIZARD_MODE.CREATION,
            isOnboarding,
          })
        )
      }

      // The thumbnail can only be created once the offer exists (POST /offers/thumbnails needs its id).
      if (offerIdRef.current && hasUpsertedImage && !isImageReadOnly) {
        try {
          await mutate(
            [GET_OFFER_QUERY_KEY, offerIdRef.current],
            handleImageOnSubmit(offerIdRef.current),
            {
              revalidate: false,
              // `thumbnailResult` is undefined when the image has been deleted.
              populateCache: (thumbnailResult, cachedOffer) => ({
                ...cachedOffer,
                thumbUrl: thumbnailResult?.url ?? '',
                activeMediation: {
                  ...cachedOffer?.activeMediation,
                  thumbUrl: thumbnailResult?.url ?? '',
                  credit: thumbnailResult?.credit ?? '',
                  alternativeText: thumbnailResult?.alternativeText ?? '',
                },
              }),
            }
          )
        } catch (error) {
          snackBar.error(
            getHumanReadableApiError(
              error,
              'Une erreur est survenue lors de l’enregistrement de votre image'
            )
          )
          return false
        }
      }

      if (mode === OFFER_WIZARD_MODE.EDITION) {
        hasSavedOfferRef.current = true
      }

      logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        offerId: offerIdRef.current,
        offerType: 'individual',
      })

      return true
    } catch (error) {
      if (isErrorAPIError(error)) {
        for (const field in error.body) {
          form.setError(field as keyof DescriptionFormValues, {
            message: error.body[field],
          })
        }
      }

      return false
    }
  }

  const readOnlyFields = getFormV2ReadOnlyFields(null, selectedPartnerVenue)

  const afterSubmitPath = () =>
    getAfterSubmitPath({
      offerId: offerIdRef.current,
      mode,
      isOnboarding,
      followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS_V2,
    })
  const afterSubmitState = () =>
    hasSavedOfferRef.current
      ? { successMessage: 'Votre offre a bien été modifiée.' }
      : undefined

  const { navigationGuardedSubmitHandler, navigationGuardDialog } =
    useFormNavigationGuard({
      afterSubmitPath,
      afterSubmitState,
      form,
      isExternallyDirty: hasUpsertedImage,
      onSubmit,
      saveAndLeaveSuccessMessage: PATCH_SUCCESS_MESSAGE,
    })

  const handlePreviousStep = () => {
    void navigate(
      isOnboarding
        ? '/onboarding/individuel'
        : '/offre/individuelle/v2/creation/nature-format-domaine'
    )
  }

  const { isDirty, isSubmitting } = form.formState

  if (!offerIdRef.current && (!nature || !format)) {
    return (
      <Navigate
        to="/offre/individuelle/v2/creation/nature-format-domaine"
        replace
      />
    )
  }

  if (isLoading) {
    return <Spinner />
  }

  return (
    <OfferCapabilityProvider capabilities={capabilities}>
      <FormProvider {...form}>
        <form onSubmit={navigationGuardedSubmitHandler}>
          <ScrollToFirstHookFormErrorAfterSubmit />
          <MandatoryInfo />
          <FormLayout>
            <FormLayout.Section title="À propos de votre offre">
              <HasCapability name={FieldEnum.TITLE_BIEN}>
                <FormLayout.Row>
                  <TextInput
                    maxCharactersCount={90}
                    label="Titre du bien"
                    {...form.register('name', {
                      disabled: readOnlyFields.includes('name'),
                    })}
                    required={mandatoryFields.includes(FieldEnum.TITLE)}
                    error={form.formState.errors.name?.message}
                    autoComplete="false"
                  />
                </FormLayout.Row>
              </HasCapability>
              <HasCapability name={FieldEnum.DESCRIPTION}>
                <FormLayout.Row>
                  <TextArea
                    label="Description"
                    description='Utilisez des doubles astérisques pour mettre en gras : **exemple** et des tirets bas pour l’italique : _exemple_. Vous pourrez vérifier l’affichage à l’étape "Récapitulatif".'
                    maxLength={10000}
                    {...form.register('description', {
                      disabled: readOnlyFields.includes('description'),
                    })}
                    required={mandatoryFields.includes(FieldEnum.DESCRIPTION)}
                    error={form.formState.errors.description?.message}
                  />
                </FormLayout.Row>
              </HasCapability>
              <IndividualOfferV2DescriptionExtraData
                readOnlyFields={readOnlyFields}
                capabilities={capabilities}
                mandatoryFields={mandatoryFields}
              />
            </FormLayout.Section>
            <HasCapability name={FieldEnum.ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT}>
              <FormLayout.Section title="Modalités d'accessibilité">
                <FormLayout.Row>
                  <CheckboxGroup
                    options={accessibilityOptions}
                    label="Sélectionnez le dispositif d'accessibilité qui correspond à votre offre :"
                    variant="detailed"
                    disabled={readOnlyFields.includes(
                      'visualDisabilityCompliant'
                    )}
                    error={
                      form.formState.errors.visualDisabilityCompliant?.message
                    }
                  />
                </FormLayout.Row>
              </FormLayout.Section>
            </HasCapability>
            <HasCapability name={FieldEnum.IMAGE}>
              <FormLayout.Section title="Illustrez votre offre">
                <FormLayout.Row>
                  <IndividualOfferV2DescriptionImage
                    displayedImage={displayedImage}
                    onImageUpload={onImageUpload}
                    onImageDelete={onImageDelete}
                    isReadOnly={isImageReadOnly}
                  />
                </FormLayout.Row>
              </FormLayout.Section>
            </HasCapability>
          </FormLayout>
          <ActionsBarSticky hasSideNav={false} isEmbedded={true}>
            <ActionsBarSticky.Left>
              <Button
                color={ButtonColor.NEUTRAL}
                variant={ButtonVariant.SECONDARY}
                onClick={handlePreviousStep}
                label="Étape précédente"
                icon={strokeLeftIcon}
                iconPosition={IconPositionEnum.LEFT}
                isLoading={isSubmitting}
              />
            </ActionsBarSticky.Left>

            <ActionsBarSticky.Right>
              <Button
                type="submit"
                color={ButtonColor.BRAND}
                variant={ButtonVariant.PRIMARY}
                label="Étape suivante"
                icon={strokeRightIcon}
                iconPosition={IconPositionEnum.RIGHT}
                disabled={
                  !isDirty &&
                  !hasUpsertedImage &&
                  mode !== OFFER_WIZARD_MODE.CREATION
                }
                isLoading={isSubmitting}
              />
            </ActionsBarSticky.Right>
          </ActionsBarSticky>
          {navigationGuardDialog}
        </form>
      </FormProvider>
    </OfferCapabilityProvider>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferV2Description
