import { FormikProvider, useFormik } from 'formik'
import React, { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { VenueProviderResponse } from 'apiClient/v1'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import {
  VenueFormValues,
  validationSchema,
  VenueForm,
} from 'components/VenueForm'
import { generateSiretValidationSchema } from 'components/VenueForm/Informations/SiretOrCommentFields'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { IOfferer } from 'core/Offerers/types'
import { IProviders, IVenue } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import { useNewOfferCreationJourney } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { MailOutlineIcon } from 'icons'
import { ReactComponent as AddOfferSvg } from 'icons/full-more.svg'
import { Button, Title } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import {
  serializeEditVenueBodyModel,
  serializePostVenueBodyModel,
} from './serializers'
import { venueSubmitRedirectUrl } from './utils/venueSubmitRedirectUrl'
import style from './VenueFormScreen.module.scss'

interface IVenueEditionProps {
  isCreatingVenue: boolean
  initialValues: VenueFormValues
  offerer: IOfferer
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  providers?: IProviders[]
  venueProviders?: VenueProviderResponse[]
  venue?: IVenue
  hasBookingQuantity?: boolean
}

const VenueFormScreen = ({
  isCreatingVenue,
  initialValues,
  offerer,
  venueTypes,
  venueLabels,
  venueProviders,
  venue,
  providers,
  hasBookingQuantity,
}: IVenueEditionProps): JSX.Element => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const [isSiretValued, setIsSiretValued] = useState(
    isCreatingVenue || !!venue?.siret
  )

  const hasNewOfferCreationJourney = useNewOfferCreationJourney()

  const isNewOnboardingActive = useActiveFeature('WIP_ENABLE_NEW_ONBOARDING')
  const isWithdrawalUpdatedMailActive = useActiveFeature(
    'WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL'
  )

  const { currentUser } = useCurrentUser()

  const [shouldSendMail, setShouldSendMail] = useState<boolean>(false)

  const [isWithdrawalDialogOpen, setIsWithdrawalDialogOpen] =
    useState<boolean>(false)

  const handleCancelWithdrawalDialog = async () => {
    setShouldSendMail(false)
    await formik.handleSubmit()
  }

  const handleConfirmWithdrawalDialog = async () => {
    await setShouldSendMail(true)
    await formik.handleSubmit()
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
      isWithdrawalUpdatedMailActive &&
      !isCreatingVenue &&
      value.isWithdrawalAppliedOnAllOffers &&
      hasBookingQuantity &&
      !handleWithdrawalDialog()
    ) {
      return
    }

    const request = isCreatingVenue
      ? api.postCreateVenue(
          serializePostVenueBodyModel(value, {
            hideSiret: !isSiretValued,
            offererId: offerer.nonHumanizedId,
          })
        )
      : api.editVenue(
          /* istanbul ignore next: there will always be a venue id on update screen */
          venue?.nonHumanizedId || 0,
          serializeEditVenueBodyModel(
            value,
            {
              hideSiret: venue?.siret.length === 0,
            },
            isWithdrawalUpdatedMailActive ? shouldSendMail : false
          )
        )

    let savedSuccess: boolean
    request
      .then(response => {
        savedSuccess = true
        navigate(
          venueSubmitRedirectUrl(
            hasNewOfferCreationJourney,
            isCreatingVenue,
            offerer.nonHumanizedId,
            // FIXME (mageoffray, 2023-06-19) : once patch response only has numeric ids we can simplify venue.id value
            // @ts-expect-error
            isCreatingVenue ? response.id : response.nonHumanizedId,
            currentUser
          )
        )

        if (!hasNewOfferCreationJourney || currentUser.isAdmin) {
          notify.success('Vos modifications ont bien été enregistrées')
        }
      })
      .catch(error => {
        savedSuccess = false
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
      })
      .finally(() => {
        logEvent?.(Events.CLICKED_SAVE_VENUE, {
          from: location.pathname,
          saved: savedSuccess,
          isEdition: !isCreatingVenue,
        })
      })
  }

  const generateSiretOrCommentValidationSchema: any = useMemo(
    () => generateSiretValidationSchema(offerer.siren, isSiretValued),
    [offerer.siren, isSiretValued]
  )

  const formValidationSchema = validationSchema(isNewOnboardingActive).concat(
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

  const { logEvent } = useAnalytics()

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
              <Button
                variant={ButtonVariant.PRIMARY}
                /* istanbul ignore next: DEBT, TO FIX */
                onClick={() =>
                  logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                    from: OFFER_FORM_NAVIGATION_IN.VENUE,
                    to: OFFER_FORM_HOMEPAGE,
                    used: OFFER_FORM_NAVIGATION_MEDIUM.VENUE_BUTTON,
                    isEdition: false,
                  })
                }
                Icon={AddOfferSvg}
              >
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
            venue && (
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
            isNewOnboardingActive={isNewOnboardingActive}
          />
        </form>
        {isWithdrawalUpdatedMailActive && isWithdrawalDialogOpen && (
          <ConfirmDialog
            cancelText="Ne pas envoyer"
            confirmText="Envoyer un email"
            leftButtonAction={handleCancelWithdrawalDialog}
            onCancel={() => setIsWithdrawalDialogOpen(false)}
            onConfirm={handleConfirmWithdrawalDialog}
            icon={MailOutlineIcon}
            title="Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?"
          />
        )}
      </FormikProvider>
    </div>
  )
}

export default VenueFormScreen
