import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import type { JSX } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useSWRConfig } from 'swr'
import * as yup from 'yup'

import { apiNew } from '@/apiClient/api'
import type { ProAdviceModel } from '@/apiClient/v1'
import { GET_OFFER_PRO_ADVICE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
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

import styles from './OfferRecommendationForm.module.scss'

interface OfferRecommendationFormProps {
  offerId: number
  proAdvice: ProAdviceModel | null
  onClose: () => void
}

interface OfferRecommendationFormValues {
  content: string
  author: string
}

const validationSchema = yup.object().shape({
  content: yup
    .string()
    .required('La recommandation est obligatoire')
    .max(800, 'La recommandation ne doit pas dépasser 800 caractères'),
  author: yup
    .string()
    .max(20, 'Le nom ne doit pas dépasser 20 caractères')
    .optional()
    .default(''),
})

export function OfferRecommendationForm({
  offerId,
  proAdvice,
  onClose,
}: Readonly<OfferRecommendationFormProps>): JSX.Element {
  const snackBar = useSnackBar()
  const { mutate } = useSWRConfig()

  const defaultValues: OfferRecommendationFormValues = {
    content: proAdvice?.content ?? '',
    author: proAdvice?.author ?? '',
  }

  const form = useForm<OfferRecommendationFormValues>({
    defaultValues,
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
        await apiNew.updateOfferProAdvice({
          path: { offer_id: offerId },
          body,
        })
      } else {
        await apiNew.createOfferProAdvice({
          path: { offer_id: offerId },
          body,
        })
      }

      await mutate([GET_OFFER_PRO_ADVICE_QUERY_KEY, offerId])
      snackBar.success('Votre recommandation a bien été ajoutée')
      onClose()
    } catch {
      snackBar.error('Une erreur est survenue lors de l’enregistrement')
    }
  }

  const onDelete = async () => {
    try {
      await apiNew.deleteOfferProAdvice({
        path: { offer_id: offerId },
      })
      await mutate([GET_OFFER_PRO_ADVICE_QUERY_KEY, offerId])
      snackBar.success('Votre recommandation a bien été supprimée')
      onClose()
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
        <p className={styles['subtitle']}>
          Les jeunes sont sensibles aux recommandations de professionnels. En
          ajoutant la vôtre, votre offre augmente ses chances d’être visualisée.
        </p>
        <div className={styles['form-content']}>
          <TextArea
            {...register('content')}
            label="Recommandation"
            required
            maxLength={800}
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
                isExternal
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
              color={ButtonColor.NEUTRAL}
              onClick={onDelete}
              label="Supprimer la recommandation"
              icon={fullTrashIcon}
            />
          </div>
        )}

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
              label="Enregistrer la recommandation"
            />
          </div>
        </DialogBuilder.Footer>
      </form>
    </FormProvider>
  )
}
