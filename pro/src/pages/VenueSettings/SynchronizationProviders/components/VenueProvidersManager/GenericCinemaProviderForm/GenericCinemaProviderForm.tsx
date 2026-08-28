import { useForm } from 'react-hook-form'

import type { PostVenueProviderBody } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { SynchronizationEvents } from '@/commons/core/FirebaseEvents/constants'
import { DuoCheckbox } from '@/components/DuoCheckbox/DuoCheckbox'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { QuantityInput } from '@/ui-kit/form/QuantityInput/QuantityInput'

import styles from './GenericCinemaProviderForm.module.scss'

export interface GenericCinemaProviderFormValues {
  isDuo: boolean
  price?: number | null
  quantity?: number | null
  isActive?: boolean
}

export interface GenericCinemaProviderFormProps {
  saveVenueProvider: (payload: PostVenueProviderBody) => Promise<boolean>
  providerId: number
  isCreationMode?: boolean
  initialValues?: GenericCinemaProviderFormValues
  onCancel?: () => void
  showAdvancedFields?: boolean // If true, show price & quantity
  formId?: string
  showFooter?: boolean
}

export const GenericCinemaProviderForm = ({
  saveVenueProvider,
  providerId,
  isCreationMode = false,
  initialValues,
  onCancel,
  showAdvancedFields = false,
  formId,
  showFooter = true,
}: GenericCinemaProviderFormProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  const onSubmit = async (formValues: GenericCinemaProviderFormValues) => {
    const payload: PostVenueProviderBody = {
      providerId,
      isDuo: formValues.isDuo,
      isActive: formValues.isActive,
    }

    if (showAdvancedFields) {
      payload.price = Number(formValues.price)
      payload.quantity = formValues.quantity
        ? Number(formValues.quantity)
        : undefined
    }

    const isSuccess = await saveVenueProvider(payload)

    logEvent(SynchronizationEvents.CLICKED_IMPORT, {
      providerId,
      saved: isSuccess,
    })
  }

  const hookForm = useForm({
    defaultValues: initialValues,
    mode: 'onChange',
  })

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { isValid, isSubmitting },
  } = hookForm

  const formValues = watch()

  return (
    <form
      id={formId}
      className={styles['cinema-provider-form']}
      data-testid="generic-cinema-provider-form"
      onSubmit={(e) => {
        e.stopPropagation()
        e.preventDefault()
        return handleSubmit(onSubmit)(e)
      }}
    >
      <div className={styles['cinema-provider-form-content']}>
        {showAdvancedFields && (
          <FormLayout.Row className={styles['form-layout-row']}>
            <div className={styles['price-input']}>
              <TextInput
                {...register('price', {
                  required: 'Veuillez renseigner un prix de vente',
                })}
                type="number"
                label="Prix de vente par place (en €)"
                min={1}
                step={0.01}
                required
              />
            </div>
            <div className={styles['nb-places-input']}>
              <QuantityInput
                min={1}
                label="Nombre de places par séance"
                value={formValues.quantity ?? undefined}
                onChange={(e) => setValue('quantity', Number(e.target.value))}
              />
            </div>
          </FormLayout.Row>
        )}

        <FormLayout.Row>
          <DuoCheckbox
            {...register('isDuo')}
            checked={Boolean(watch('isDuo'))}
          />
        </FormLayout.Row>

        {showAdvancedFields && (
          <div className={styles['allocine-provider-form-banner']}>
            <Banner
              variant={isCreationMode ? undefined : BannerVariants.WARNING}
              title={
                isCreationMode
                  ? 'Séances “classiques” uniquement'
                  : 'Modifications applicables uniquement sur les nouvelles offres'
              }
              description={
                isCreationMode
                  ? 'Seules les séances “classiques” peuvent être importées pour le moment. Les séances spécifiques (3D, Dolby Atmos, 4DX...) seront bientôt disponibles.'
                  : 'Les modifications s’appliqueront uniquement aux nouvelles offres créées. La modification doit être faite manuellement pour les offres existantes.'
              }
            />
          </div>
        )}
      </div>

      {showFooter && (
        <footer className={styles['cinema-provider-form-footer']}>
          {isCreationMode ? (
            <Button
              type="submit"
              isLoading={isSubmitting}
              disabled={!isValid}
              label="Lancer la synchronisation"
            />
          ) : (
            <div className={styles['cinema-provider-form-buttons']}>
              <Button
                variant={ButtonVariant.SECONDARY}
                color={ButtonColor.NEUTRAL}
                onClick={onCancel}
                type="button"
                label="Annuler"
              />
              <Button
                type="submit"
                variant={ButtonVariant.PRIMARY}
                isLoading={isSubmitting}
                disabled={!isValid}
                label="Modifier"
              />
            </div>
          )}
        </footer>
      )}
    </form>
  )
}
