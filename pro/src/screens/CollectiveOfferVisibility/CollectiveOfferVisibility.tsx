import { Banner, SelectAutocomplete, SubmitButton } from 'ui-kit'
import {
  EducationalInstitutionResponseModel,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import { FormikProvider, useFormik } from 'formik'
import { Link, useParams } from 'react-router-dom'
import { Mode, VisibilityFormValues } from 'core/OfferEducational'
import React, { useEffect, useState } from 'react'

import FormLayout from 'new_components/FormLayout'
import { PatchEducationalInstitutionAdapter } from 'routes/CollectiveOfferVisibility/adapters/patchEducationalInstitutionAdapter'
import RadioGroup from 'ui-kit/form/RadioGroup'
import Spinner from 'components/layout/Spinner'
import { computeOffersUrl } from 'core/Offers/utils'
import { extractInitialVisibilityValues } from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import styles from './CollectiveOfferVisibility.module.scss'
import useNotification from 'components/hooks/useNotification'
import validationSchema from './validationSchema'

export interface CollectiveOfferVisibilityProps {
  patchInstitution: PatchEducationalInstitutionAdapter
  mode: Mode
  initialValues: VisibilityFormValues
  onSuccess: ({
    offerId,
    message,
    payload,
  }: {
    offerId: string
    message: string
    payload: GetCollectiveOfferResponseModel
  }) => void
  institutions: EducationalInstitutionResponseModel[]
  isLoadingInstitutions: boolean
}
interface InstitutionOption extends SelectOption {
  postalCode?: string
  city?: string
  name: string
  institutionType?: string
}

const CollectiveOfferVisibility = ({
  mode,
  patchInstitution,
  initialValues,
  onSuccess,
  institutions,
  isLoadingInstitutions,
}: CollectiveOfferVisibilityProps) => {
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()

  const onSubmit = async (values: VisibilityFormValues) => {
    setButtonPressed(true)
    const result = await patchInstitution({
      offerId,
      institutionId: values.visibility === 'all' ? null : values.institution,
      isCreatingOffer: mode === Mode.CREATION,
    })

    if (!result.isOk) {
      setButtonPressed(false)
      return notify.error(result.message)
    }

    onSuccess({
      offerId,
      message: result.message ?? '',
      payload: result.payload,
    })
    setButtonPressed(false)
    formik.resetForm({
      values: extractInitialVisibilityValues(result.payload.institution),
    })
  }

  const formik = useFormik<VisibilityFormValues>({
    initialValues,
    onSubmit,
    validationSchema,
  })

  const [institutionsOptions, setInstitutionsOptions] =
    useState<InstitutionOption[]>()

  const [selectedInstitution, setSelectedInstitution] =
    useState<InstitutionOption | null>()

  const [buttonPressed, setButtonPressed] = useState(false)

  useEffect(() => {
    setInstitutionsOptions(
      institutions.map(({ name, id, city, postalCode, institutionType }) => ({
        label: `${institutionType ?? ''} ${name} - ${city}`.trim(),
        value: String(id),
        city,
        postalCode,
        name,
        institutionType: institutionType ?? '',
      }))
    )
  }, [institutions])

  useEffect(() => {
    if (formik.values.institution) {
      const selected = institutionsOptions?.find(
        institution => institution.value === formik.values.institution
      )
      setSelectedInstitution(selected)
    } else {
      setSelectedInstitution(null)
    }
  }, [formik.values.institution, institutionsOptions])

  const noInstitutionSelected =
    formik.values.visibility === 'one' && formik.values.institution.length === 0
  const userHasNotUpdatedForm =
    mode === Mode.EDITION &&
    !(['visibility', 'institution'] as const).some(
      key => formik.values[key] !== formik.initialValues[key]
    )
  const nextStepDisabled =
    buttonPressed ||
    noInstitutionSelected ||
    userHasNotUpdatedForm ||
    mode === Mode.READ_ONLY

  return (
    <FormikProvider value={formik}>
      <form onSubmit={formik.handleSubmit}>
        <FormLayout>
          <FormLayout.Section title="Visibilité de l’offre">
            <p className={styles['description-text']}>
              Les établissements concernés par vos choix seront les seuls à
              pouvoir visualiser et/ou préréserver votre offre sur ADAGE. Vous
              avez jusqu’à la préréservation d’un enseignant pour modifier la
              visibilité de votre offre.
            </p>
            <FormLayout.Row className={styles['row-layout']}>
              <fieldset className={styles['legend']}>
                1. Qui peut visualiser votre offre ?
              </fieldset>
              <RadioGroup
                disabled={mode === Mode.READ_ONLY}
                group={[
                  {
                    label: 'Tous les établissements',
                    value: 'all',
                  },
                  {
                    label: 'Un établissement en particulier',
                    value: 'one',
                  },
                ]}
                name="visibility"
                withBorder
              />
            </FormLayout.Row>
            {institutionsOptions && formik.values.visibility === 'one' && (
              <FormLayout.Row
                className={(styles['row-layout'], styles['row-layout-large'])}
              >
                <fieldset className={styles['legend']}>
                  2. Choix de l’établissement
                </fieldset>
                {isLoadingInstitutions ? (
                  <Spinner />
                ) : (
                  <>
                    <SelectAutocomplete
                      fieldName="institution"
                      options={institutionsOptions}
                      label="Établissement scolaire"
                      placeholder="Saisir l’établissement scolaire"
                      maxDisplayOptions={20}
                      maxDisplayOptionsLabel="20 résultats maximum. Veuillez affiner votre recherche"
                      maxHeight={100}
                      hideArrow
                    />
                    {selectedInstitution && (
                      <Banner type="light" className={styles['institution']}>
                        {`${selectedInstitution.institutionType} ${selectedInstitution.name}`.trim()}
                        <br />
                        {`${selectedInstitution.postalCode} ${selectedInstitution.city}`}
                      </Banner>
                    )}
                  </>
                )}
              </FormLayout.Row>
            )}
          </FormLayout.Section>

          <FormLayout.Actions className={styles['actions-layout']}>
            <Link className="secondary-link" to={computeOffersUrl({})}>
              Annuler et quitter
            </Link>
            <SubmitButton
              className=""
              disabled={nextStepDisabled}
              isLoading={false}
            >
              {mode === Mode.CREATION
                ? 'Valider et créer l’offre'
                : 'Valider et enregistrer l’offre'}
            </SubmitButton>
          </FormLayout.Actions>
        </FormLayout>
      </form>
    </FormikProvider>
  )
}

export default CollectiveOfferVisibility
