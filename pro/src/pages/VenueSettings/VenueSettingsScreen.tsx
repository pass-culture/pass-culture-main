import { FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import {
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { GET_VENUE_QUERY_KEY } from 'config/swrQueryKeys'
import { Events } from 'core/FirebaseEvents/constants'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared/constants'
import { SelectOption } from 'custom_types/form'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useNotification } from 'hooks/useNotification'
import fullBackIcon from 'icons/full-back.svg'
import strokeErrorIcon from 'icons/stroke-error.svg'
import strokeMailIcon from 'icons/stroke-mail.svg'
import { generateSiretValidationSchema } from 'pages/VenueCreation/SiretOrCommentFields/validationSchema'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { serializeEditVenueBodyModel } from './serializers'
import { VenueSettingsFormValues } from './types'
import { getValidationSchema } from './validationSchema'
import { VenueSettingsForm } from './VenueSettingsForm'
import styles from './VenueSettingsScreen.module.scss'

interface VenueSettingsScreenProps {
  initialValues: VenueSettingsFormValues
  offerer: GetOffererResponseModel
  venueLabels: SelectOption[]
  venueTypes: VenueTypeResponseModel[]
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueSettingsScreen = ({
  initialValues,
  offerer,
  venueLabels,
  venueTypes,
  venueProviders,
  venue,
}: VenueSettingsScreenProps): JSX.Element => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const [isSiretValued, setIsSiretValued] = useState(Boolean(venue.siret))
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()

  const { currentUser } = useCurrentUser()

  const [shouldSendMail, setShouldSendMail] = useState(false)
  const [isWithdrawalDialogOpen, setIsWithdrawalDialogOpen] = useState(false)
  const [isAddressChangeDialogOpen, setIsAddressChangeDialogOpen] =
    useState(false)

  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const handleCancelWithdrawalDialog = () => {
    setShouldSendMail(false)
    formik.handleSubmit()
  }

  const handleConfirmWithdrawalDialog = () => {
    setShouldSendMail(true)
    formik.handleSubmit()
  }

  const handleCancelAddressChangeDialog = () => {
    setIsAddressChangeDialogOpen(false)
  }

  const handleConfirmAddressChangeDialog = () => {
    setIsAddressChangeDialogOpen(true)
    formik.handleSubmit()
  }

  const handleWithdrawalDialog = () => {
    const valueMeta = formik.getFieldMeta('withdrawalDetails')
    if (valueMeta.touched && valueMeta.value !== valueMeta.initialValue) {
      if (isWithdrawalDialogOpen) {
        setIsWithdrawalDialogOpen(false)
      } else {
        setIsWithdrawalDialogOpen(true)
        return false
      }
    }
    return true
  }

  const handleDialogAddressChange = () => {
    const latitudeMeta = formik.getFieldMeta('latitude')
    const longitudeMeta = formik.getFieldMeta('longitude')
    const coordsMeta = formik.getFieldMeta('coords')
    const streetMeta = formik.getFieldMeta('street')
    const postalCodeMeta = formik.getFieldMeta('postalCode')
    const cityMeta = formik.getFieldMeta('city')

    // If any of the address fields changed, we should display the dialog
    if (
      (latitudeMeta.touched &&
        latitudeMeta.value !== latitudeMeta.initialValue) ||
      (longitudeMeta.touched &&
        longitudeMeta.value !== longitudeMeta.initialValue) ||
      (postalCodeMeta.touched &&
        postalCodeMeta.value !== postalCodeMeta.initialValue) ||
      (coordsMeta.touched && coordsMeta.value !== coordsMeta.initialValue) ||
      (cityMeta.touched && cityMeta.value !== cityMeta.initialValue) ||
      (streetMeta.touched && streetMeta.value !== streetMeta.initialValue)
    ) {
      if (isAddressChangeDialogOpen) {
        setIsAddressChangeDialogOpen(false)
      } else {
        setIsAddressChangeDialogOpen(true)
        return false
      }
    }
    return true
  }

  const onSubmit = async (values: VenueSettingsFormValues) => {
    if (
      (values.isWithdrawalAppliedOnAllOffers && !handleWithdrawalDialog()) ||
      (!handleDialogAddressChange() && isOfferAddressEnabled)
    ) {
      return
    }

    try {
      await api.editVenue(
        venue.id,
        serializeEditVenueBodyModel(values, !venue.siret, shouldSendMail)
      )
      await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])

      navigate(`/structures/${venue.managingOfferer.id}/lieux/${venue.id}`)

      if (currentUser.isAdmin) {
        notify.success(PATCH_SUCCESS_MESSAGE)
      }

      logEvent(Events.CLICKED_SAVE_VENUE, {
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

      logEvent(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: false,
        isEdition: true,
      })
    }
  }
  const formValidationSchema = getValidationSchema(venue.isVirtual).concat(
    generateSiretValidationSchema(
      venue.isVirtual,
      isSiretValued,
      offerer.siren,
      initialValues.siret
    )
  )

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmit,
    validationSchema: formValidationSchema,
  })

  return (
    <>
      <Button
        variant={ButtonVariant.TERNARYPINK}
        icon={fullBackIcon}
        onClick={() => navigate(-1)}
      >
        Retour vers la page précédente
      </Button>

      <h1 className={styles['title']}>Paramètres généraux</h1>

      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <VenueSettingsForm
            updateIsSiretValued={setIsSiretValued}
            venueLabels={venueLabels}
            venueTypes={venueTypes}
            venueProviders={venueProviders}
            venue={venue}
            offerer={offerer}
          />
        </form>

        <ConfirmDialog
          cancelText="Ne pas envoyer"
          confirmText="Envoyer un email"
          leftButtonAction={handleCancelWithdrawalDialog}
          onCancel={() => setIsWithdrawalDialogOpen(false)}
          onConfirm={handleConfirmWithdrawalDialog}
          icon={strokeMailIcon}
          title="Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?"
          open={isWithdrawalDialogOpen}
        />
        {isOfferAddressEnabled && (
          <ConfirmDialog
            cancelText="Annuler"
            confirmText="Confirmer le changement d'adresse"
            leftButtonAction={handleCancelAddressChangeDialog}
            onCancel={() => setIsAddressChangeDialogOpen(false)}
            onConfirm={handleConfirmAddressChangeDialog}
            icon={strokeErrorIcon}
            title="Ce changement d'adresse ne va pas s'impacter sur vos offres"
            open={isAddressChangeDialogOpen && venue.hasOffers}
          >
            <p>
              Si vous souhaitez rectifier leur localisation, vous devez les
              modifier individuellement.
            </p>
          </ConfirmDialog>
        )}
      </FormikProvider>
    </>
  )
}
