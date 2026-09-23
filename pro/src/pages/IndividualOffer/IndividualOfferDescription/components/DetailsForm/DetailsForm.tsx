import { yupResolver } from '@hookform/resolvers/yup'
import { useRef } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  CategoryResponseModel,
  SubcategoryResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { updateAccessibilityField } from '@/commons/utils/updateAccessibilityField'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MarkdownInfoBox } from '@/components/MarkdownInfoBox/MarkdownInfoBox'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { getAfterSubmitPath } from '@/pages/IndividualOffer/commons/utils/getAfterSubmitPath'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import { DEFAULT_DETAILS_FORM_VALUES } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/constants'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/types'
import {
  getFormReadOnlyFields,
  isSubCategoryCD,
} from '@/pages/IndividualOffer/IndividualOfferDescription/commons/utils'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import {
  serializeDetailsPatchData,
  serializeDetailsPostData,
} from '../../commons/serializers'
import { getValidationSchema } from '../../commons/validationSchema'
import { DetailsSubForm } from './DetailsSubForm/DetailsSubForm'
import { Subcategories } from './Subcategories/Subcategories'

type DetailsFormProps = {
  initialValues: DetailsFormValues
  isEanSearchDisplayed: boolean
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
  canClaimCulturalOutreach: boolean
  setSubcategoryId: (subcategoryId: string | undefined) => void
}

export const DetailsForm = ({
  initialValues,
  isEanSearchDisplayed,
  filteredCategories,
  filteredSubcategories,
  canClaimCulturalOutreach,
  setSubcategoryId,
}: DetailsFormProps): JSX.Element => {
  const { offer: initialOffer, hasPublishedOfferWithSameEan } =
    useIndividualOfferContext()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const mode = useOfferWizardMode()
  const offerIdRef = useRef(initialOffer?.id)
  // Read by `afterSubmitState` so the success message is shown once the
  // destination page (or this same page) has taken over, instead of racing with the navigation.
  const hasSavedOfferRef = useRef(false)
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const navigate = useNavigate()
  const isNewOfferDraft = !initialOffer

  const form = useForm<DetailsFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver<DetailsFormValues, unknown, unknown>(
      // @ts-expect-error
      getValidationSchema()
    ),
    mode: 'onBlur',
  })

  const onSubmit = async (formValues: DetailsFormValues): Promise<boolean> => {
    try {
      if (offerIdRef.current) {
        await mutate(
          [GET_OFFER_QUERY_KEY, offerIdRef.current],
          api.patchOffer({
            path: { offer_id: offerIdRef.current },
            body: serializeDetailsPatchData(formValues, readOnlyFields),
          }),
          { revalidate: false }
        )
      } else {
        await mutate(
          [GET_OFFER_QUERY_KEY],
          api.createOffer({ body: serializeDetailsPostData(formValues) }),
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
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
            offerId: offerIdRef.current,
            mode: OFFER_WIZARD_MODE.CREATION,
            isOnboarding,
          })
        )
      }

      if (mode === OFFER_WIZARD_MODE.EDITION) {
        hasSavedOfferRef.current = true
      }

      logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        offerId: offerIdRef.current,
        offerType: 'individual',
        subcategoryId: form.getValues('subcategoryId'),
      })

      return true
    } catch (error) {
      if (isErrorAPIError(error)) {
        for (const field in error.body) {
          form.setError(field as keyof DetailsFormValues, {
            message: error.body[field],
          })
        }
      }

      return false
    }
  }

  const afterSubmitPath = () =>
    getAfterSubmitPath({
      offerId: offerIdRef.current,
      mode,
      isOnboarding,
      followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
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
      onSubmit,
    })

  const handlePreviousStep = () => {
    navigate(isOnboarding ? '/onboarding/individuel' : '/offre/creation')
  }

  // const {
  //   formState: { errors },
  //   register,
  //   setValue,
  //   watch,
  // } = useFormContext<DetailsFormValues>()
  const subcategoryId = form.watch('subcategoryId')
  const accessibility = form.watch('accessibility')

  const isSubCategorySelected =
    subcategoryId !== DEFAULT_DETAILS_FORM_VALUES.subcategoryId

  const accessibilityOptions = updateAccessibilityField(
    form.setValue,
    accessibility
  )
  const hasSelectedProduct = !!form.watch('productId')

  const readOnlyFields = getFormReadOnlyFields(
    initialOffer,
    hasSelectedProduct,
    selectedPartnerVenue
  )

  return (
    <FormProvider {...form}>
      <form onSubmit={navigationGuardedSubmitHandler}>
        <ScrollToFirstHookFormErrorAfterSubmit />
        <FormLayout fullWidthActions>
          <FormLayout.Section title="À propos de votre offre">
            <FormLayout.Row>
              <TextInput
                maxCharactersCount={90}
                label="Titre de l’offre"
                {...form.register('name')}
                error={form.formState.errors.name?.message}
                required
                disabled={readOnlyFields.includes('name')}
                // This is so browsers don't raise any issue / improvement
                // regarding the existence of an <input type="text" name="name" />
                // that isnt about an user's name to be autofilled.
                autoComplete="false"
              />
            </FormLayout.Row>
            {canClaimCulturalOutreach && (
              <FormLayout.Row mdSpaceAfter>
                <CheckboxGroup
                  label="Action de médiation"
                  variant="detailed"
                  disabled={readOnlyFields.includes('hasCulturalOutreachClaim')}
                  error={
                    form.formState.errors.hasCulturalOutreachClaim?.message
                  }
                  options={[
                    {
                      label:
                        'L’offre inclut une action de médiation spécifique',
                      description:
                        'Ex : rencontre avec des artistes, ateliers participatifs, comité de spectacteurs...',
                      checked: Boolean(form.watch('hasCulturalOutreachClaim')),
                      onChange: (e) =>
                        form.setValue(
                          'hasCulturalOutreachClaim',
                          e.target.checked,
                          {
                            shouldDirty: true,
                          }
                        ),
                    },
                  ]}
                />
              </FormLayout.Row>
            )}
            <FormLayout.Row sideComponent={<MarkdownInfoBox />}>
              <TextArea
                label="Description"
                maxLength={10000}
                {...form.register('description')}
                disabled={readOnlyFields.includes('description')}
                error={form.formState.errors.description?.message}
              />
            </FormLayout.Row>
          </FormLayout.Section>
          <Subcategories
            readOnlyFields={readOnlyFields}
            filteredCategories={filteredCategories}
            filteredSubcategories={filteredSubcategories}
            setSubcategoryId={setSubcategoryId}
          />
          {isSubCategorySelected && (
            <DetailsSubForm
              isEanSearchDisplayed={isEanSearchDisplayed}
              isProductBased={hasSelectedProduct}
              isOfferCD={isSubCategoryCD(subcategoryId)}
              readOnlyFields={readOnlyFields}
            />
          )}
          {accessibilityOptions && (
            <FormLayout.Section title="Modalités d’accessibilité">
              <FormLayout.Row>
                <CheckboxGroup
                  options={accessibilityOptions}
                  disabled={readOnlyFields.includes('accessibility')}
                  label="Cette offre est accessible au public en situation de handicap :"
                  description="Sélectionnez au moins une option"
                  variant="detailed"
                  error={form.formState.errors.accessibility?.message}
                />
              </FormLayout.Row>
            </FormLayout.Section>
          )}
        </FormLayout>
        <ActionBar
          dirtyForm={form.formState.isDirty || isNewOfferDraft}
          isDisabled={
            form.formState.isSubmitting ||
            Boolean(initialOffer && isOfferDisabled(initialOffer)) ||
            hasPublishedOfferWithSameEan ||
            (!form.formState.isDirty && mode !== OFFER_WIZARD_MODE.CREATION)
          }
          onClickPrevious={handlePreviousStep}
          step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION}
        />
        {navigationGuardDialog}
      </form>
    </FormProvider>
  )
}
