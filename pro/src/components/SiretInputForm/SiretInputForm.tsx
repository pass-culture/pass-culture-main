import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

import type { StructureDataBodyModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { FORM_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { getSiretData } from '@/commons/core/Venue/utils/getSiretData'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { unhumanizeSiret } from '@/commons/utils/siren'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { BannerInvisibleSiren } from '@/components/SignupJourneyForm/Offerer/BannerInvisibleSiren/BannerInvisibleSiren'
import { validationSchema } from '@/components/SignupJourneyForm/Offerer/validationSchema'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'

export interface OffererFormValues {
  siret: string
}

type SiretInputProps = {
  submitElement: (isSubmitting: boolean) => JSX.Element
  initialValues: OffererFormValues
  beforeCallCheck?: (formValues: OffererFormValues) => void
  handleSiretData: (
    formValues: OffererFormValues,
    offererSiretData: StructureDataBodyModel
  ) => void
}

export const SiretInputForm = ({
  initialValues,
  submitElement,
  beforeCallCheck,
  handleSiretData,
}: SiretInputProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  const snackBar = useSnackBar()
  const [showInvisibleBanner, setShowInvisibleBanner] = useState<boolean>(false)

  const hookForm = useForm({
    resolver: yupResolver(validationSchema),
    defaultValues: initialValues,
    mode: 'onBlur',
  })

  const {
    register,
    setValue,
    handleSubmit,
    setError,
    watch,
    formState: { errors, isSubmitting },
  } = hookForm

  if (isSubmitting && Object.keys(errors).length !== 0) {
    snackBar.error(FORM_ERROR_MESSAGE)
  }

  const onSubmit = async (formValues: OffererFormValues): Promise<void> => {
    beforeCallCheck?.(formValues)

    // If we're here, it means the siret we've just submitted is different from the one already stored in localStorage

    let offererSiretData: StructureDataBodyModel

    try {
      offererSiretData = await getSiretData(unhumanizeSiret(formValues.siret))

      if (!offererSiretData) {
        snackBar.error('Une erreur est survenue')
        return
      }
    } catch (error) {
      if (error instanceof Error) {
        setShowInvisibleBanner(
          error.message ===
            "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public"
        )
        setError('siret', { message: error.message })
      }
      return
    }
    handleSiretData(formValues, offererSiretData)
  }

  return (
    <FormLayout>
      <form onSubmit={handleSubmit(onSubmit)} data-testid="signup-offerer-form">
        <FormLayout.Section>
          <FormLayout.Row mdSpaceAfter>
            <TextInput
              {...register('siret')}
              label="Numéro de SIRET à 14 chiffres"
              type="text"
              required
              error={errors.siret?.message}
              onChange={(e) => {
                if (
                  watch('siret').length === 0 ||
                  e.target.value.replace(/(\d|\s)*/, '').length > 0 ||
                  e.target.value.length === 14
                ) {
                  setValue('siret', unhumanizeSiret(e.target.value))
                }
              }}
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <Button
              as="a"
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              to="https://annuaire-entreprises.data.gouv.fr/"
              isExternal
              opensInNewTab
              onClick={() => logEvent(Events.CLICKED_UNKNOWN_SIRET)}
              label="Vous ne connaissez pas votre SIRET ? Consultez l'Annuaire des Entreprises."
            />
          </FormLayout.Row>
        </FormLayout.Section>
        {showInvisibleBanner && <BannerInvisibleSiren />}
        <Banner
          title="Vous êtes un équipement d’une collectivité ou d’un établissement public ?"
          actions={[
            {
              href: 'https://aide.passculture.app/hc/fr/articles/4633420022300--Acteurs-Culturels-Collectivit%C3%A9-Lieu-rattach%C3%A9-%C3%A0-une-collectivit%C3%A9-S-inscrire-et-param%C3%A9trer-son-compte-pass-Culture-',
              label: 'En savoir plus',
              isExternal: true,
              type: 'link',
              icon: fullLinkIcon,
              iconAlt: 'Nouvelle fenêtre',
            },
          ]}
          description={
            <p>
              Renseignez le SIRET de la structure à laquelle vous êtes rattaché.
            </p>
          }
        />
        {submitElement(isSubmitting)}
      </form>
    </FormLayout>
  )
}
