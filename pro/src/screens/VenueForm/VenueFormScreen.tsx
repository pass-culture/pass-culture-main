import { FormikProvider, useFormik } from 'formik'
import React, { useMemo, useState } from 'react'
import { useHistory } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import {
  GetVenueResponseModel,
  VenueProviderResponse,
  VenueResponseModel,
} from 'apiClient/v1'
import {
  IVenueFormValues,
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
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'
import { Button, Title } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import {
  serializeEditVenueBodyModel,
  serializePostVenueBodyModel,
} from './serializers'
import style from './VenueFormScreen.module.scss'

interface IVenueEditionProps {
  isCreatingVenue: boolean
  initialValues: IVenueFormValues
  offerer: IOfferer
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  providers?: IProviders[]
  venueProviders?: VenueProviderResponse[]
  venue?: IVenue
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
}: IVenueEditionProps): JSX.Element => {
  const history = useHistory()
  const notify = useNotification()
  const [isSiretValued, setIsSiretValued] = useState(
    isCreatingVenue || !!venue?.siret
  )
  const isNewBankInformationCreation = useActiveFeature(
    'ENABLE_NEW_BANK_INFORMATIONS_CREATION'
  )
  const { currentUser } = useCurrentUser()

  const onSubmit = async (value: IVenueFormValues) => {
    const request = isCreatingVenue
      ? api.postCreateVenue(
          serializePostVenueBodyModel(value, {
            hideSiret: !isSiretValued,
            offererId: offerer.id,
          })
        )
      : api.editVenue(
          /* istanbul ignore next: there will always be a venue id on update screen */
          venue?.id || '',
          serializeEditVenueBodyModel(value, { hideSiret: !!venue?.comment })
        )

    request
      .then((response: VenueResponseModel | GetVenueResponseModel) => {
        notify.success('Vos modifications ont bien été enregistrées')

        const venuesUrl = currentUser.isAdmin
          ? `/structures/${offerer.id}`
          : '/accueil'
        history.push(
          isCreatingVenue
            ? `/structures/${offerer.id}/lieux/${response.id}`
            : venuesUrl,
          isNewBankInformationCreation
        )
      })
      .catch(error => {
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
        <Title level={2} className={style['venueName']}>
          {initialIsVirtual
            ? `${offerer.name} (Offre numérique)`
            : publicName || initialName}
        </Title>
        {!isCreatingVenue &&
          isNewBankInformationCreation &&
          venue &&
          venue.dmsToken && (
            <>
              {/* For the screen reader to spell-out the id, we add a
                visually hidden span with a space between each character.
                The other span will be hidden from the screen reader. */}
              <span className={style['identifier-hidden']}>
                N° d'identifiant du lieu : {venue.dmsToken.split('').join(' ')}
              </span>
              <span aria-hidden={true}>
                N° d'identifiant du lieu : {venue.dmsToken}
              </span>
            </>
          )}
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
          />
        </form>
      </FormikProvider>
    </div>
  )
}

export default VenueFormScreen
