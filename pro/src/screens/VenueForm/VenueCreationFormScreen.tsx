import { FormikProvider, useFormik } from 'formik'
import { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { VenueProviderResponse } from 'apiClient/v1'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import {
  validationSchema,
  VenueForm,
  VenueFormValues,
} from 'components/VenueForm'
import { generateSiretValidationSchema } from 'components/VenueForm/Informations/SiretOrCommentFields'
import { Events } from 'core/FirebaseEvents/constants'
import { Offerer } from 'core/Offerers/types'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared'
import { Providers, Venue } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import fullPlusIcon from 'icons/full-more.svg'
import strokeMailIcon from 'icons/stroke-mail.svg'
import { Button, Title } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import {
  serializeEditVenueBodyModel,
  serializePostVenueBodyModel,
} from './serializers'
import { venueSubmitRedirectUrl } from './utils/venueSubmitRedirectUrl'
import style from './VenueCreationFormScreen.module.scss'

interface VenueEditionProps {
  isCreatingVenue: boolean
  initialValues: VenueFormValues
  offerer: Offerer
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  providers?: Providers[]
  venueProviders?: VenueProviderResponse[]
  venue?: Venue
  hasBookingQuantity?: boolean
}

export const VenueCreationFormScreen = ({
  isCreatingVenue,
  initialValues,
  offerer,
  venueTypes,
  venueLabels,
  venueProviders,
  venue,
  providers,
  hasBookingQuantity,
}: VenueEditionProps): JSX.Element => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const [isSiretValued, setIsSiretValued] = useState(
    isCreatingVenue || !!venue?.siret
  )

  const { logEvent } = useAnalytics()

  const { currentUser } = useCurrentUser()

  const [shouldSendMail, setShouldSendMail] = useState<boolean>(false)

  const [isWithdrawalDialogOpen, setIsWithdrawalDialogOpen] =
    useState<boolean>(false)

  const isNewBankDetailsEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

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
      !isCreatingVenue &&
      value.isWithdrawalAppliedOnAllOffers &&
      hasBookingQuantity &&
      !handleWithdrawalDialog()
    ) {
      return
    }

    try {
      if (isCreatingVenue) {
        await api.postCreateVenue(
          serializePostVenueBodyModel(value, {
            hideSiret: !isSiretValued,
            offererId: offerer.id,
          })
        )
      } else {
        await api.editVenue(
          /* istanbul ignore next: there will always be a venue id on update screen */
          venue?.id || 0,
          serializeEditVenueBodyModel(
            value,
            {
              hideSiret: venue?.siret.length === 0,
            },
            shouldSendMail
          )
        )
      }

      navigate(venueSubmitRedirectUrl(isCreatingVenue, offerer.id, currentUser))

      if (currentUser.isAdmin) {
        notify.success(PATCH_SUCCESS_MESSAGE)
      }

      logEvent?.(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: true,
        isEdition: !isCreatingVenue,
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
        isEdition: !isCreatingVenue,
      })
    }
  }

  const generateSiretOrCommentValidationSchema: any = useMemo(
    () => generateSiretValidationSchema(offerer.siren, isSiretValued),
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

  const {
    id: initialId,
    isVirtual: initialIsVirtual,
    publicName: publicName,
    name: initialName,
  } = venue || {}

  return (
    <div>
      <div className={style['venue-form-heading']}>
        <div className={style['title-page']}>
          <Title level={1}>
            {isCreatingVenue ? 'Création d’un lieu' : 'Lieu'}
          </Title>
          {!isCreatingVenue && (
            <a
              href={`/offre/creation?lieu=${initialId}&structure=${offerer.id}`}
            >
              <Button variant={ButtonVariant.PRIMARY} icon={fullPlusIcon}>
                <span>Créer une offre</span>
              </Button>
            </a>
          )}
        </div>
        <Title level={2} className={style['venue-name']}>
          {
            /* istanbul ignore next: DEBT, TO FIX */ initialIsVirtual
              ? `${offerer.name} (Offre numérique)`
              : publicName || initialName
          }
        </Title>
        {
          /* istanbul ignore next: DEBT, TO FIX */ !isCreatingVenue &&
            venue &&
            !isNewBankDetailsEnabled && (
              <>
                {/* For the screen reader to spell-out the id, we add a
                visually hidden span with a space between each character.
                The other span will be hidden from the screen reader. */}
                <span className={style['identifier-hidden']}>
                  Identifiant du lieu : {venue.dmsToken.split('').join(' ')}
                </span>
                <span aria-hidden={true}>
                  Identifiant du lieu : {venue.dmsToken}
                </span>
              </>
            )
        }
      </div>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <VenueForm
            isCreatingVenue={isCreatingVenue}
            updateIsSiretValued={setIsSiretValued}
            venueTypes={venueTypes}
            venueLabels={venueLabels}
            venueProvider={venueProviders}
            provider={providers}
            venue={venue}
            offerer={offerer}
            initialIsVirtual={initialIsVirtual}
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
    </div>
  )
}
