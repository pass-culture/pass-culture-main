import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { apiNew } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import {
  CollectiveOfferAllowedAction,
  type GetCollectiveOfferResponseModel,
} from '@/apiClient/v1/new'
import { GET_COLLECTIVE_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { MAX_PRICE_DETAILS_LENGTH } from '@/commons/core/OfferEducational/constants'
import { Mode } from '@/commons/core/OfferEducational/types'
import { getCollectiveOfferLink } from '@/commons/core/OfferEducational/utils/getCollectiveOfferLink'
import { FORM_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { objectEntries, objectFromEntries } from '@/commons/utils/object'
import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { FormContactNew } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/OfferEducationalForm/FormContact/FormContactNew'
import { FormNotifications } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/OfferEducationalForm/FormNotifications/FormNotifications'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import {
  type CollectiveOfferInformationFormValues,
  validationSchema,
} from './validationSchema'

type CollectiveOfferInformationsFormProps = {
  offer: GetCollectiveOfferResponseModel
}

export const CollectiveOfferInformationsForm = ({
  offer,
}: CollectiveOfferInformationsFormProps): JSX.Element => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const location = useLocation()
  const { mutate } = useSWRConfig()

  const isCreation = !location.pathname.includes('edition')
  const { requete: requestId } = queryParamsFromOfferer(location)
  const canEditDetails = offer.allowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
  )

  const stepUrls = {
    previous: isCreation
      ? `/offre/${offer.id}/collectif/stocks`
      : getCollectiveOfferLink(offer.id, offer.displayedStatus),
    next: `/offre/${offer.id}/collectif/etablissement`,
  }

  if (requestId) {
    stepUrls.previous += `?requete=${requestId}`
    stepUrls.next += `?requete=${requestId}`
  }
  const defaultValues: CollectiveOfferInformationFormValues = {
    bookingEmails:
      offer.bookingEmails.length > 0
        ? offer.bookingEmails?.map((email) => ({ email }))
        : [{ email: '' }],
    contactEmail: offer.contactEmail,
    contactPhone: offer.contactPhone,
    additionalDetails: offer.additionalDetails ?? '',
  }

  const form = useForm<CollectiveOfferInformationFormValues>({
    defaultValues,
    resolver: yupResolver(validationSchema),
  })

  const onSubmit = async (formValues: CollectiveOfferInformationFormValues) => {
    try {
      const payload = objectFromEntries(
        objectEntries(form.formState.dirtyFields)
          .filter(([_, isDirty]) => isDirty)
          .map(([key, _]) => [key, formValues[key]])
      )

      if ('bookingEmails' in payload) {
        payload.bookingEmails = payload.bookingEmails.map(
          ({ email }: Record<'email', string>) => email
        )
      }

      const response = await apiNew.editCollectiveOffer({
        path: { offer_id: offer.id },
        body: payload,
      })

      await mutate<GetCollectiveOfferResponseModel>(
        [GET_COLLECTIVE_OFFER_QUERY_KEY, Number(offer.id)],
        { ...offer, ...response },
        { revalidate: false }
      )
      navigate(stepUrls.next)
    } catch (e) {
      console.error(e)
      if (isErrorAPIError(e) && e.status === 400) {
        snackBar.error(FORM_ERROR_MESSAGE)
      } else {
        snackBar.error(
          "Une erreur est survenue lors de l'enregistrement de votre offre."
        )
      }
    }
  }

  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormLayout fullWidthActions>
          <FormLayout.MandatoryInfo />
          <FormNotifications disableForm={!canEditDetails} />
          <FormContactNew disableForm={!canEditDetails} />
          <FormLayout.Section title="Informations pratiques">
            <FormLayout.Row>
              <TextArea
                disabled={!canEditDetails}
                label={'Informations pratiques sur votre offre'}
                maxLength={MAX_PRICE_DETAILS_LENGTH}
                {...form.register('additionalDetails')}
                description={'Par exemple : Informations logistiques'}
                error={form.formState.errors.additionalDetails?.message}
              />
            </FormLayout.Row>
          </FormLayout.Section>
        </FormLayout>

        <ActionsBarSticky>
          <ActionsBarSticky.Left>
            <Button
              as="a"
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              to={stepUrls.previous}
              label={isCreation ? 'Retour' : 'Annuler et quitter'}
            />
          </ActionsBarSticky.Left>
          <ActionsBarSticky.Right
            dirtyForm={form.formState.isDirty || !offer}
            mode={isCreation ? Mode.CREATION : Mode.EDITION}
          >
            <Button
              type="submit"
              disabled={!canEditDetails || form.formState.isSubmitting}
              isLoading={form.formState.isSubmitting}
              label="Enregistrer et continuer"
            />
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      </form>

      <RouteLeavingGuardCollectiveOfferCreation
        when={form.formState.isDirty && !form.formState.isSubmitting}
      />
    </FormProvider>
  )
}
