import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { SYNCHRONIZED_OFFER_EDITABLE_FIELDS } from 'core/Offers/constants'
import { IOfferIndividual } from 'core/Offers/types'
import { isAllocineOffer } from 'core/Providers/utils/localProvider'

import { serializePatchOffer } from './serializers'

type TSuccessPayload = { id: string }
type TFailurePayload = { errors: Record<string, string> }
export type TUpdateIndividualOffer = Adapter<
  { offer: IOfferIndividual; formValues: IOfferIndividualFormValues },
  TSuccessPayload,
  TFailurePayload
>

const updateIndividualOffer: TUpdateIndividualOffer = async ({
  offer,
  formValues,
}) => {
  /* istanbul ignore next: DEBT, TO FIX */
  try {
    let sentValues: Partial<IOfferIndividualFormValues> = formValues
    if (offer?.lastProvider) {
      const {
        ALLOCINE: allocineEditableFields,
        ALL_PROVIDERS: allProvidersEditableFields,
      } = SYNCHRONIZED_OFFER_EDITABLE_FIELDS

      const asArray = Object.entries(formValues)
      const editableFields = isAllocineOffer(offer)
        ? [...allocineEditableFields, ...allProvidersEditableFields]
        : allProvidersEditableFields

      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const filtered = asArray.filter(([key, value]) =>
        editableFields.includes(key)
      )

      sentValues = Object.fromEntries(filtered)
    }

    const response = await api.patchOffer(
      offer.id,
      serializePatchOffer(sentValues)
    )
    return {
      isOk: true,
      message: '',
      payload: {
        id: response.id,
      },
    }
  } catch (error) {
    let formErrors = {}
    if (isErrorAPIError(error)) {
      formErrors = error.body
    }
    const apiFieldsMap: Record<string, string> = {
      venue: 'venueId',
    }
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la création de votre offre',
      payload: {
        errors: serializeApiErrors(formErrors, apiFieldsMap),
      },
    }
  }
}

export default updateIndividualOffer
