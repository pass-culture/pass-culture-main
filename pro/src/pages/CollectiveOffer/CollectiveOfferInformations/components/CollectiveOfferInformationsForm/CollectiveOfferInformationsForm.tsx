import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'

import {
  CollectiveOfferAllowedAction,
  type GetCollectiveOfferResponseModel,
  type PatchCollectiveOfferBodyModel,
} from '@/apiClient/v1/new'
import { MAX_PRICE_DETAILS_LENGTH } from '@/commons/core/OfferEducational/constants'
import { Mode } from '@/commons/core/OfferEducational/types'
import { objectEntries, objectFromEntries } from '@/commons/utils/object'
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

export type CollectiveOfferInformationsFormProps = {
  offer: GetCollectiveOfferResponseModel
  isCreation: boolean
  saveAndContinue: (
    partialOffer: PatchCollectiveOfferBodyModel
  ) => Promise<void>
  goBackLink: string
}

export const CollectiveOfferInformationsForm = ({
  offer,
  isCreation,
  saveAndContinue,
  goBackLink,
}: CollectiveOfferInformationsFormProps): JSX.Element => {
  const canEditDetails = offer.allowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
  )

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

  const onSubmit = (formValues: CollectiveOfferInformationFormValues) => {
    const partialOffer = objectFromEntries(
      objectEntries(form.formState.dirtyFields)
        .filter(([_, isDirty]) => isDirty)
        .map(([key, _]) => [key, formValues[key]])
    )

    if ('bookingEmails' in partialOffer) {
      partialOffer.bookingEmails = partialOffer.bookingEmails.map(
        ({ email }: Record<'email', string>) => email
      )
    }
    saveAndContinue(partialOffer)
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
              to={goBackLink}
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
