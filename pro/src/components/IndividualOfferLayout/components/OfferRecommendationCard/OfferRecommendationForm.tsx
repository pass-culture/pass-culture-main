import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import type { JSX } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useSWRConfig } from 'swr'
import * as yup from 'yup'

import { api } from '@/apiClient/api'
import type { ProAdviceModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_OFFER_EXPOSURE_QUERY_KEY,
  GET_OFFER_PRO_ADVICE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullTrashIcon from '@/icons/full-trash.svg'
import { CGU_LINK } from '@/pages/IndividualOffer/IndividualOfferPracticalInfos/components/IndividualOfferPracticalInfosForm/constants'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import phoneImg from './assets/phone.png'
import styles from './OfferRecommendationForm.module.scss'

interface OfferRecommendationFormProps {
  offerId: number
  proAdvice: ProAdviceModel | null
  onSuccess: () => void
  submitLabel?: string
}

interface OfferRecommendationFormValues {
  content: string
  author: string
}

const validationSchema = yup.object().shape({
  content: yup
    .string()
    .required('La recommandation est obligatoire')
    .max(500, 'La recommandation ne doit pas dépasser 500 caractères'),
  author: yup
    .string()
    .max(20, 'Le nom ne doit pas dépasser 20 caractères')
    .optional()
    .default(''),
})

export function OfferRecommendationForm({
  offerId,
  proAdvice,
  onSuccess,
  submitLabel,
}: Readonly<OfferRecommendationFormProps>): JSX.Element {
  const snackBar = useSnackBar()
  const { mutate } = useSWRConfig()
  const { logEvent } = useAnalytics()

  const defaultValues: OfferRecommendationFormValues = {
    content: proAdvice?.content ?? '',
    author: proAdvice?.author ?? '',
  }

  const form = useForm<OfferRecommendationFormValues>({
    defaultValues,
    values: defaultValues,
    resolver: yupResolver(validationSchema),
    mode: 'onChange',
  })

  const {
    register,
    handleSubmit,
    formState: { isSubmitting, errors },
  } = form

  const onSubmit = async (values: OfferRecommendationFormValues) => {
    try {
      const body = {
        content: values.content,
        author: values.author || null,
      }

      if (proAdvice) {
        await api.updateOfferProAdvice({
          path: { offer_id: offerId },
          body,
        })
      } else {
        await api.createOfferProAdvice({
          path: { offer_id: offerId },
          body,
        })
      }

      await mutate([GET_OFFER_PRO_ADVICE_QUERY_KEY, offerId])
      await mutate([GET_OFFER_EXPOSURE_QUERY_KEY, offerId])
      logEvent(EngagementEvents.HAS_MADE_RECOMMENDATION, {
        offerId,
        action: 'validated',
      })
      snackBar.success(
        `Votre recommandation a bien été ${proAdvice ? 'modifiée' : 'ajoutée'}`
      )
      onSuccess()
    } catch {
      snackBar.error('Une erreur est survenue lors de l’enregistrement')
    }
  }

  const onDelete = async () => {
    try {
      await api.deleteOfferProAdvice({
        path: { offer_id: offerId },
      })
      await mutate([GET_OFFER_PRO_ADVICE_QUERY_KEY, offerId])
      await mutate([GET_OFFER_EXPOSURE_QUERY_KEY, offerId])
      snackBar.success('Votre recommandation a bien été supprimée')
      logEvent(EngagementEvents.HAS_MADE_RECOMMENDATION, {
        offerId,
        action: 'deleted',
      })
      onSuccess()
    } catch {
      snackBar.error('Une erreur est survenue lors de la suppression')
    }
  }

  return (
    <FormProvider {...form}>
      <form
        onSubmit={handleSubmit(onSubmit)}
        className={styles['form']}
        noValidate
      >
        <div className={styles['form-subcontainer']}>
          <div className={styles['form-content-container']}>
            <p className={styles['subtitle']}>
              La recommandation écrite est un gage de réassurance pour les
              jeunes. Celle-ci s’affiche sur votre offre et booste sa visibilité
              sur l’application.
            </p>
            <div className={styles['recommandation-header']}>
              <div>
                <img src={phoneImg} alt="Affichage sur l’offre" />
                <span
                  aria-hidden={true}
                  className={styles['recommandation-header-image-caption']}
                >
                  Affichage sur l’offre
                </span>
              </div>
              <div className={styles['recommandation-header-side']}>
                <p className={styles['recommandation-header-title']}>
                  Exemples issus d’autres offres de la même catégorie :
                </p>
                <q className={styles['recommandation-header-citation']}>
                  Une aventure mystérieuse qui va vous émerveiller. Les
                  illustrations sont à couper le souffle. Plongez !
                </q>
                <q className={styles['recommandation-header-citation']}>
                  Bluffant de maîtrise et de drôlerie, aussi fin que juste,
                  sensible que mordant.
                </q>
              </div>
            </div>
            <div className={styles['form-content']}>
              <TextArea
                {...register('content')}
                label="Recommandation"
                required
                requiredIndicator="explicit"
                maxLength={500}
                error={errors.content?.message}
              />

              <TextInput
                {...register('author')}
                label="Recommandée par :"
                maxCharactersCount={20}
                error={errors.author?.message}
              />
              <p className={styles['form-cgu']}>
                En publiant cette recommandation, vous acceptez qu’elle soit
                diffusée sur l’application conformément à nos{' '}
                <span className={styles['cgu-link']}>
                  <Button
                    as="a"
                    variant={ButtonVariant.TERTIARY}
                    opensInNewTab
                    to={CGU_LINK}
                    color={ButtonColor.NEUTRAL}
                    size={ButtonSize.SMALL}
                    label={'conditions générales d’utilisation.'}
                  />
                </span>
              </p>
            </div>
            {proAdvice && (
              <div className={styles['form-delete']}>
                <Button
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.DANGER}
                  onClick={onDelete}
                  label="Supprimer la recommandation"
                  icon={fullTrashIcon}
                />
              </div>
            )}
          </div>
          <div className={styles['form-footer-container']}>
            <DialogBuilder.Footer>
              <div className={styles['form-footer']}>
                <Dialog.Close asChild>
                  <Button
                    variant={ButtonVariant.SECONDARY}
                    color={ButtonColor.NEUTRAL}
                    label="Fermer"
                  />
                </Dialog.Close>
                <Button
                  type="submit"
                  isLoading={isSubmitting}
                  label={submitLabel ?? 'Enregistrer la recommandation'}
                />
              </div>
            </DialogBuilder.Footer>
          </div>
        </div>
      </form>
    </FormProvider>
  )
}
