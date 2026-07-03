import { yupResolver } from '@hookform/resolvers/yup'
import { useFieldArray, useForm } from 'react-hook-form'
import { useLocation } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import {
  CollectiveOfferAllowedAction,
  type GetCollectiveOfferResponseModel,
} from '@/apiClient/v1'
import { GET_COLLECTIVE_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { MAX_PRICE_DETAILS_LENGTH } from '@/commons/core/OfferEducational/constants'
import { Mode } from '@/commons/core/OfferEducational/types'
import { getCollectiveOfferLink } from '@/commons/core/OfferEducational/utils/getCollectiveOfferLink'
import { PATCH_SUCCESS_MESSAGE } from '@/commons/core/shared/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { objectEntries, objectFromEntries } from '@/commons/utils/object'
import { queryParamsFromOfferer } from '@/commons/utils/queryParamsFromOfferer'
import { sendSentryCustomError } from '@/commons/utils/sendSentryCustomError'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import styles from './CollectiveOfferInformationForm.module.scss'
import {
  type CollectiveOfferInformationFormValues,
  validationSchema,
} from './validationSchema'

export type CollectiveOfferInformationFormProps = {
  offer: GetCollectiveOfferResponseModel
}

export const CollectiveOfferInformationForm = ({
  offer,
}: CollectiveOfferInformationFormProps): JSX.Element => {
  const canEditDetails = offer.allowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
  )
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const location = useLocation()
  const snackBar = useSnackBar()
  const { mutate } = useSWRConfig()

  const { requete: requestId } = queryParamsFromOfferer(location)
  const isEdition = location.pathname.includes('edition')

  const defaultValues: CollectiveOfferInformationFormValues = {
    bookingEmails:
      offer.bookingEmails.length > 0
        ? offer.bookingEmails?.map((email) => ({ email }))
        : [{ email: selectedPartnerVenue.collectiveEmail ?? '' }],
    contactEmail: offer.contactEmail ?? selectedPartnerVenue.collectiveEmail,
    contactPhone:
      offer.contactPhone ??
      // We use contactEmail (which is required) to know if we already saved
      // the phone as empty or if it's the first time we see this form
      (offer.contactEmail ? '' : selectedPartnerVenue.collectivePhone),
    additionalDetails: offer.additionalDetails ?? '',
  }

  const form = useForm<CollectiveOfferInformationFormValues>({
    defaultValues,
    resolver: yupResolver(validationSchema),
  })
  const { fields, remove, append } = useFieldArray({
    control: form.control,
    name: 'bookingEmails',
  })

  const onSubmit = async (
    formValues: CollectiveOfferInformationFormValues
  ): Promise<boolean> => {
    const dirtyFields = form.formState.dirtyFields
    const partialOffer = objectFromEntries(
      objectEntries(dirtyFields)
        .filter(([_, isDirty]) => isDirty)
        .map(([key, _]) => [key, formValues[key]])
    )

    // We ensure that fields initialized with venue are saved if not dirty
    if (!dirtyFields.bookingEmails && offer.bookingEmails.length === 0) {
      partialOffer.bookingEmails = formValues.bookingEmails
    }
    if (
      !dirtyFields.contactEmail &&
      offer.contactEmail !== formValues.contactEmail
    ) {
      partialOffer.contactEmail = formValues.contactEmail
    }
    if (
      !dirtyFields.contactPhone &&
      offer.contactPhone !== formValues.contactPhone
    ) {
      partialOffer.contactPhone = formValues.contactPhone
    }

    if ('bookingEmails' in partialOffer) {
      partialOffer.bookingEmails = partialOffer.bookingEmails.map(
        ({ email }: Record<'email', string>) => email
      )
    }

    try {
      const updatedOffer = await api.editCollectiveOffer({
        path: { offer_id: offer.id },
        body: partialOffer,
      })

      await mutate<GetCollectiveOfferResponseModel>(
        [GET_COLLECTIVE_OFFER_QUERY_KEY, Number(offer.id)],
        // TODO (igabriele, 2026-07-02): Moved as-is but it doesn't look like a partial response, so why do we merge it with the original?
        { ...offer, ...updatedOffer },
        { revalidate: false }
      )

      snackBar.success(PATCH_SUCCESS_MESSAGE)

      return true
    } catch (e) {
      if (isErrorAPIError(e) && e.status < 500) {
        serializeApiErrors(e.body, form.setError)
      } else {
        sendSentryCustomError(e)

        snackBar.error(
          "Une erreur est survenue lors de l'enregistrement de votre offre."
        )
      }

      return false
    }
  }

  function removeBookingEmail(index: number) {
    return () => {
      remove(index)
      form.setFocus(`bookingEmails.${index - 1}.email`)
    }
  }

  // We need to force dirty field evaluation at render
  // since fieldArray.remove does not dirty the field by itself properly
  const _bookingEmailsDirty = form.formState.dirtyFields.bookingEmails
  const stepUrls = {
    previous: `/offre/${offer.id}/collectif/stocks`,
    next: `/offre/${offer.id}/collectif/etablissement`,
  }
  if (isEdition) {
    stepUrls.previous = getCollectiveOfferLink(offer.id, offer.displayedStatus)
    stepUrls.next = getCollectiveOfferLink(offer.id, offer.displayedStatus)
  }
  if (requestId) {
    stepUrls.previous += `?requete=${requestId}`
    stepUrls.next += `?requete=${requestId}`
  }
  const { navigationGuardDialog, navigationGuardedSubmitHandler } =
    useFormNavigationGuard({
      afterSubmitPath: stepUrls.next,
      form,
      onSubmit,
    })

  return (
    <form onSubmit={navigationGuardedSubmitHandler}>
      <FormLayout fullWidthActions>
        <FormLayout.MandatoryInfo />
        <FormLayout.Section
          title="À quel email le pass Culture peut-il vous envoyer des notifications ?"
          className={styles['booking-emails-section']}
        >
          {fields.map((field, index) => (
            <FormLayout.Row key={field.id}>
              <TextInput
                {...form.register(`bookingEmails.${index}.email` as const)}
                description="Format : email@exemple.com"
                disabled={!canEditDetails}
                error={
                  form.formState.errors.bookingEmails?.[index]?.email?.message
                }
                extension={
                  index > 0 &&
                  canEditDetails && (
                    <Button
                      variant={ButtonVariant.SECONDARY}
                      color={ButtonColor.NEUTRAL}
                      onClick={removeBookingEmail(index)}
                      icon={fullTrashIcon}
                      tooltip="Supprimer l’email"
                    />
                  )
                }
                label="Email auquel envoyer les notifications"
                required
              />
            </FormLayout.Row>
          ))}
          {canEditDetails && fields.length <= 5 && (
            <Button
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              icon={fullMoreIcon}
              onClick={() => {
                append({ email: '' }, { shouldFocus: true })
              }}
              label="Ajouter un email de notification"
            />
          )}
        </FormLayout.Section>
        <FormLayout.Section title="Comment les enseignants peuvent-ils vous contacter ?">
          <FormLayout.Row className={styles['phone-number-row']}>
            <PhoneNumberInput
              {...form.register('contactPhone')}
              disabled={!canEditDetails}
              error={form.formState.errors.contactPhone?.message}
              label="Téléphone"
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <TextInput
              {...form.register('contactEmail')}
              description="Format : email@exemple.com"
              disabled={!canEditDetails}
              error={form.formState.errors.contactEmail?.message}
              label="Email"
              required
              type="email"
            />
          </FormLayout.Row>
        </FormLayout.Section>
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
            label={isEdition ? 'Annuler et quitter' : 'Retour'}
          />
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right
          dirtyForm={form.formState.isDirty || !offer}
          mode={isEdition ? Mode.EDITION : Mode.CREATION}
        >
          <Button
            type="submit"
            disabled={!canEditDetails || form.formState.isSubmitting}
            isLoading={form.formState.isSubmitting}
            label="Enregistrer et continuer"
          />
        </ActionsBarSticky.Right>
      </ActionsBarSticky>

      {navigationGuardDialog}
    </form>
  )
}
