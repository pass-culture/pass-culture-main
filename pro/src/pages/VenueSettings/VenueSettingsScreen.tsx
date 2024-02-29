import { FormikProvider, useFormik } from 'formik'
import { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import {
  VenueProviderResponse,
  GetOffererResponseModel,
  GetVenueResponseModel,
} from 'apiClient/v1'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { VenueFormValues } from 'components/VenueCreationForm'
import { generateSiretValidationSchema } from 'components/VenueCreationForm/Informations/SiretOrCommentFields'
import { validationSchema } from 'components/VenueCreationForm/validationSchema'
import { Events } from 'core/FirebaseEvents/constants'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared'
import { Providers } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import fullBackIcon from 'icons/full-back.svg'
import strokeMailIcon from 'icons/stroke-mail.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { serializeEditVenueBodyModel } from './serializers'
import { VenueSettingsForm } from './VenueSettingsForm'
import styles from './VenueSettingsScreen.module.scss'

interface VenueSettingsFormScreenProps {
  initialValues: VenueFormValues
  offerer: GetOffererResponseModel
  venueTypes: SelectOption[]
  providers?: Providers[]
  venueProviders?: VenueProviderResponse[]
  venue: GetVenueResponseModel
  hasBookingQuantity?: boolean
}

export const VenueSettingsFormScreen = ({
  initialValues,
  offerer,
  venueTypes,
  venueProviders,
  venue,
  providers,
  hasBookingQuantity,
}: VenueSettingsFormScreenProps): JSX.Element => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const [isSiretValued, setIsSiretValued] = useState(Boolean(venue.siret))
  const { logEvent } = useAnalytics()

  const { currentUser } = useCurrentUser()

  const [shouldSendMail, setShouldSendMail] = useState<boolean>(false)

  const [isWithdrawalDialogOpen, setIsWithdrawalDialogOpen] =
    useState<boolean>(false)

  const handleCancelWithdrawalDialog = () => {
    setShouldSendMail(false)
    formik.handleSubmit()
  }

  const handleConfirmWithdrawalDialog = () => {
    setShouldSendMail(true)
    formik.handleSubmit()
  }

  const handleWithdrawalDialog = () => {
    const valueMeta = formik.getFieldMeta('withdrawalDetails')
    if (
      valueMeta &&
      valueMeta.touched &&
      valueMeta.value != valueMeta.initialValue
    ) {
      if (isWithdrawalDialogOpen) {
        setIsWithdrawalDialogOpen(false)
      } else {
        setIsWithdrawalDialogOpen(true)
        return false
      }
    }
    return true
  }

  const onSubmit = async (value: VenueFormValues) => {
    if (
      value.isWithdrawalAppliedOnAllOffers &&
      hasBookingQuantity &&
      !handleWithdrawalDialog()
    ) {
      return
    }

    try {
      await api.editVenue(
        /* istanbul ignore next: there will always be a venue id on update screen */
        venue?.id || 0,
        serializeEditVenueBodyModel(
          value,
          {
            // siret is not filled in initial values it could be empty
            // for venues without siret
            hideSiret: value.siret.length === 0,
          },
          shouldSendMail
        )
      )

      navigate('/accueil')

      if (currentUser.isAdmin) {
        notify.success(PATCH_SUCCESS_MESSAGE)
      }

      logEvent?.(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: true,
        isEdition: true,
      })
    } catch (error) {
      let formErrors
      if (isErrorAPIError(error)) {
        formErrors = error.body
      }
      const apiFieldsMap: Record<string, string> = {
        venue: 'venueId',
        venueTypeCode: 'venueType',
        venueLabelId: 'venueLabel',
        'contact.email': 'email',
        'contact.phoneNumber': 'phoneNumber',
        'contact.website': 'webSite',
        address: 'search-addressAutocomplete',
        visualDisabilityCompliant: 'accessibility.visual',
        mentalDisabilityCompliant: 'accessibility.mental',
        motorDisabilityCompliant: 'accessibility.motor',
        audioDisabilityCompliant: 'accessibility.audio',
      }

      if (!formErrors || Object.keys(formErrors).length === 0) {
        notify.error('Erreur inconnue lors de la sauvegarde du lieu.')
      } else {
        notify.error(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )
        formik.setErrors(serializeApiErrors(formErrors, apiFieldsMap))
        formik.setStatus('apiError')
      }

      logEvent?.(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: false,
        isEdition: true,
      })
    }
  }

  const generateSiretOrCommentValidationSchema: any = useMemo(
    () => generateSiretValidationSchema(isSiretValued, offerer.siren),
    [offerer.siren, isSiretValued]
  )

  const formValidationSchema = validationSchema.concat(
    generateSiretOrCommentValidationSchema
  )

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmit,
    validationSchema: formValidationSchema,
  })

  return (
    <>
      <ButtonLink
        variant={ButtonVariant.TERNARYPINK}
        icon={fullBackIcon}
        link={{
          to: `/structures/${offerer.id}/lieux/${venue.id}`,
        }}
      >
        Retour vers la page partenaire
      </ButtonLink>

      <h1 className={styles['title']}>Paramètres de l’activité</h1>

      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <VenueSettingsForm
            updateIsSiretValued={setIsSiretValued}
            venueTypes={venueTypes}
            venueProvider={venueProviders}
            provider={providers}
            venue={venue}
            offerer={offerer}
          />
        </form>

        {isWithdrawalDialogOpen && (
          <ConfirmDialog
            cancelText="Ne pas envoyer"
            confirmText="Envoyer un email"
            leftButtonAction={handleCancelWithdrawalDialog}
            onCancel={() => setIsWithdrawalDialogOpen(false)}
            onConfirm={handleConfirmWithdrawalDialog}
            icon={strokeMailIcon}
            title="Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?"
          />
        )}
      </FormikProvider>
    </>
  )
}
