import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { type JSX, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import useSWR, { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import {
  GET_HIGHLIGHTS_QUERY_KEY,
  GET_OFFER_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useNotification } from '@/commons/hooks/useNotification'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import styles from './OfferHighlightBanner.module.scss'
import type { OfferHighlightFormValues } from './types'
import { validationSchema } from './validationSchema'

interface OfferHighlightBannerProps {
  offerId: number
}

export const OfferHighlightBanner = ({
  offerId,
}: OfferHighlightBannerProps): JSX.Element => {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const notify = useNotification()
  const { mutate } = useSWRConfig()

  const highlightQuery = useSWR(
    [GET_HIGHLIGHTS_QUERY_KEY],
    () => api.getHighlights(),
    { fallbackData: [] }
  )

  const onSubmit = async (values: OfferHighlightFormValues) => {
    try {
      await mutate(
        [GET_OFFER_QUERY_KEY, offerId],
        api.postHighlightRequestOffer(offerId, {
          highlight_ids: values.highlightIds,
        }),
        { revalidate: false }
      )
      setIsDialogOpen(false)
    } catch {
      notify.error(
        'Une erreur est survenue lors de la selection des temps forts'
      )
    }
  }

  const form = useForm<OfferHighlightFormValues>({
    defaultValues: { highlightIds: [] },
    resolver: yupResolver<OfferHighlightFormValues, unknown, unknown>(
      validationSchema
    ),
    mode: 'onBlur',
  })

  const { watch, setValue } = form

  return (
    <Callout variant={CalloutVariant.INFO}>
      Valorisez votre évènement en l’associant à un temps fort.
      <div>
        <DialogBuilder
          trigger={
            <Button variant={ButtonVariant.TERNARY}>
              Choisir un temps fort
            </Button>
          }
          open={isDialogOpen}
          onOpenChange={setIsDialogOpen}
          title="Choisir un temps fort"
          variant="drawer"
        >
          <FormProvider {...form}>
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className={styles['form']}
              noValidate
            >
              <div className={styles['form-content']}>
                <Callout
                  variant={CalloutVariant.INFO}
                  title="Pré-requis pour être sélectionnée par notre équipe éditoriale :"
                >
                  <div className={styles['form-info-callout']}>
                    <ul>
                      <li>L'offre est liée à la thématique choisie</li>
                      <li>L'offre se déroule pendant le temps fort</li>
                      <li>L'offre est au statut publiée</li>
                      <li>L'offre a une image</li>
                    </ul>
                    <p>
                      Un email de validation vous sera envoyé au moment de la
                      valorisation sur l’application.
                    </p>
                  </div>
                </Callout>
                <CheckboxGroup
                  options={highlightQuery.data.map((highlight) => {
                    const selected = watch('highlightIds') ?? []
                    const isChecked = selected.includes(highlight.id)
                    return {
                      name: String(highlight.id),
                      label: highlight.name,
                      description: highlight.description,
                      checked: isChecked,
                      onChange: (e) => {
                        const current = watch('highlightIds') ?? []
                        const next = e.target.checked
                          ? Array.from(new Set([...current, highlight.id]))
                          : current.filter((id: number) => id !== highlight.id)
                        setValue('highlightIds', next, {
                          shouldValidate: true,
                        })
                      },
                    }
                  })}
                  label="Les prochains temps forts :"
                  labelTag="h3"
                  variant="detailed"
                />
              </div>
              <DialogBuilder.Footer>
                <div className={styles['form-footer']}>
                  <Dialog.Close asChild>
                    <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
                  </Dialog.Close>
                  <Button type="submit">Valider la sélection</Button>
                </div>
              </DialogBuilder.Footer>
            </form>
          </FormProvider>
        </DialogBuilder>
      </div>
    </Callout>
  )
}
