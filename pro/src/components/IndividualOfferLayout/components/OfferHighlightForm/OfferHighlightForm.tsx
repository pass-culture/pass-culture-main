import * as Dialog from '@radix-ui/react-dialog'
import type { JSX } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import useSWR, { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type { ShortHighlightResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_HIGHLIGHTS_QUERY_KEY,
  GET_OFFER_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { HighlightEvents } from '@/commons/core/FirebaseEvents/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { HighlightDatespanTag } from '@/components/HighlightDatespanTag/HighlightDatespanTag'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './OfferHighlightForm.module.scss'
import type { OfferHighlightFormValues } from './types'

interface OfferHighlightFormProps {
  offerId: number
  onSuccess: () => void
  highlightRequests: Array<ShortHighlightResponseModel>
}

export function OfferHighlightForm({
  offerId,
  onSuccess,
  highlightRequests,
}: OfferHighlightFormProps): JSX.Element {
  const snackBar = useSnackBar()
  const { mutate } = useSWRConfig()
  const { logEvent } = useAnalytics()

  const defaultValues = {
    highlightIds: highlightRequests.map((request) => request.id),
  }

  const highlightQuery = useSWR(
    [GET_HIGHLIGHTS_QUERY_KEY],
    () => api.getHighlights(),
    { fallbackData: [] }
  )

  const form = useForm<OfferHighlightFormValues>({
    defaultValues,
  })

  const {
    watch,
    setValue,
    formState: { isDirty, isSubmitting },
  } = form

  const onSubmit = async (values: OfferHighlightFormValues) => {
    try {
      await mutate(
        [GET_OFFER_QUERY_KEY, offerId],
        await api.postHighlightRequestOffer(offerId, {
          highlight_ids: values.highlightIds,
        }),
        { revalidate: false }
      )
      logEvent(HighlightEvents.HAS_VALIDATED_HIGHLIGHT, {
        offerId,
        highlightIds: values.highlightIds,
      })
      onSuccess()
      if (isDirty) {
        const successMessage =
          values.highlightIds.length > 0
            ? 'La sélection des temps forts a bien été prise en compte'
            : 'Les temps forts ont été dissociés'
        snackBar.success(successMessage)
      }
    } catch {
      snackBar.error(
        'Une erreur est survenue lors de la sélection des temps forts'
      )
    }
  }

  if (highlightQuery.isLoading) {
    return <Spinner />
  }

  return (
    <FormProvider {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className={styles['form']}
        noValidate
      >
        <div className={styles['form-content']}>
          <Banner
            variant={BannerVariants.DEFAULT}
            title="Pré-requis pour être sélectionnée par notre équipe éditoriale :"
            description={
              <div className={styles['form-info-callout']}>
                <ul className={styles['form-info-callout-list']}>
                  <li>- L’offre est liée à la thématique choisie</li>
                  <li>- L’offre se déroule pendant le temps fort</li>
                  <li>- L’offre est au statut publiée</li>
                  <li>- L’offre a une image</li>
                </ul>
                <p>
                  Un email de validation vous sera envoyé au moment de la
                  valorisation sur l’application.
                </p>
              </div>
            }
          />

          <CheckboxGroup
            label="Les prochains temps forts :"
            variant="detailed"
            error={form.formState.errors.highlightIds?.message}
            options={highlightQuery.data.map((highlight) => {
              const selectedHighlightIds = watch('highlightIds') ?? []
              const isChecked = selectedHighlightIds.includes(highlight.id)

              return {
                name: `highlight-form-checkbox-${highlight.id}`,
                label: highlight.name,
                description: highlight.description,
                checked: isChecked,
                sizing: 'fill',
                asset: {
                  variant: 'tag',
                  tag: {
                    label: (
                      <HighlightDatespanTag
                        highlightDatespan={highlight.highlightDatespan}
                      />
                    ),
                  },
                },
                onChange: (e) => {
                  const next = e.target.checked
                    ? [
                        ...new Set([...selectedHighlightIds, highlight.id]),
                      ].sort()
                    : selectedHighlightIds.filter((id) => id !== highlight.id)
                  setValue('highlightIds', next, { shouldDirty: true })
                },
              }
            })}
          />
        </div>
        <DialogBuilder.Footer>
          <div className={styles['form-footer']}>
            <Dialog.Close asChild>
              <Button
                variant={ButtonVariant.SECONDARY}
                color={ButtonColor.NEUTRAL}
                label="Annuler"
              />
            </Dialog.Close>
            <Button
              type="submit"
              isLoading={isSubmitting}
              label="Valider la sélection"
            />
          </div>
        </DialogBuilder.Footer>
      </form>
    </FormProvider>
  )
}
