import { FormikProvider, useFormik } from 'formik'
import { Link, useHistory, useParams } from 'react-router-dom'
import React, { useEffect, useState } from 'react'
import { SelectAutocomplete, SubmitButton } from 'ui-kit'

import FormLayout from 'new_components/FormLayout'
import { GetEducationalInstitutionsAdapter } from 'routes/CollectiveOfferVisibility/adapters/getEducationalInstitutionsAdapter'
import { Mode } from 'core/OfferEducational'
import { PatchEducationalInstitutionAdapter } from 'routes/CollectiveOfferVisibility/adapters/patchEducationalInstitutionAdapter'
import RadioGroup from 'ui-kit/form/RadioGroup'
import { computeOffersUrl } from 'core/Offers/utils'
import { extractOfferIdAndOfferTypeFromRouteParams } from 'core/OfferEducational'
import styles from './CollectiveOfferVisibility.module.scss'
import useNotification from 'components/hooks/useNotification'
import validationSchema from './validationSchema'

export interface CollectiveOfferVisibilityProps {
  getInstitutions: GetEducationalInstitutionsAdapter
  patchInstitution: PatchEducationalInstitutionAdapter
  mode: Mode
}
interface InstitutionOption extends SelectOption {
  postalCode?: string
  city?: string
}

const CollectiveOfferVisibility = ({
  getInstitutions,
  mode,
  patchInstitution,
}: CollectiveOfferVisibilityProps) => {
  const formik = useFormik({
    initialValues: {
      visibility: 'all',
      institution: '',
      'search-institution': '',
    },
    onSubmit: () => {},
    validationSchema,
  })

  const notify = useNotification()
  const history = useHistory()

  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)

  const [institutionsOptions, setInstitutionsOptions] =
    useState<InstitutionOption[]>()

  const [buttonPressed, setButtonPressed] = useState(false)

  const handleSubmit = () => {
    setButtonPressed(true)
    const successUrl = `/offre/${offerId}/collectif/confirmation`
    if (formik.values.visibility === 'one') {
      patchInstitution({
        offerId,
        institutionId: formik.values.institution,
      }).then(result => {
        if (result.isOk) {
          history.push(successUrl)
        } else {
          notify.error(result.message)
          setButtonPressed(false)
        }
      })
    } else {
      // if visibility === 'all' nothing to save
      history.push(successUrl)
    }
  }

  useEffect(() => {
    getInstitutions().then(res => {
      if (res.isOk)
        setInstitutionsOptions(
          res.payload.institutions.map(({ name, id, city, postalCode }) => ({
            label: name,
            value: String(id),
            city,
            postalCode,
          }))
        )
    })
  }, [])

  return (
    <FormikProvider value={formik}>
      <form
        onSubmit={e => {
          handleSubmit()
          e.preventDefault()
        }}
      >
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
              <FormLayout.Row className={styles['row-layout']}>
                <fieldset className={styles['legend']}>
                  2. Choix de l’établissement
                </fieldset>
                <SelectAutocomplete
                  fieldName="institution"
                  options={institutionsOptions}
                  label="Établissement scolaire"
                  maxDisplayOptions={20}
                  maxDisplayOptionsLabel="20 résultats maximum. Veuillez affiner votre recherche"
                  maxHeight={100}
                />
              </FormLayout.Row>
            )}
            {formik.values.institution && <></>}
          </FormLayout.Section>

          <FormLayout.Actions className={styles['actions-layout']}>
            <Link className="secondary-link" to={computeOffersUrl({})}>
              Annuler et quitter
            </Link>
            <SubmitButton
              className=""
              disabled={
                buttonPressed ||
                (formik.values.visibility === 'one' &&
                  formik.values.institution.length === 0)
              }
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
