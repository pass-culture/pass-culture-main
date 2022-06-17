import { FormikProvider, useFormik } from 'formik'
import { Link, useHistory, useParams } from 'react-router-dom'
import { MultiSelectAutocomplete, SubmitButton } from 'ui-kit'
import React, { useEffect, useState } from 'react'

import FormLayout from 'new_components/FormLayout'
import { GetEducationalInstitutionsAdapter } from 'routes/CollectiveOfferVisibility/adapters/getEducationalInstitutionsAdapter'
import { Mode } from 'core/OfferEducational'
import { PatchEducationalInstitutionAdapter } from 'routes/CollectiveOfferVisibility/adapters/patchEducationalInstitutionAdapter'
import RadioGroup from 'ui-kit/form/RadioGroup'
import { SelectOption } from 'custom_types/form'
import { computeOffersUrl } from 'core/Offers/utils'
import { extractOfferIdAndOfferTypeFromRouteParams } from 'core/OfferEducational'
import styles from './CollectiveOfferVisibility.module.scss'
import useNotification from 'components/hooks/useNotification'
import validationSchema from './validationSchema'

interface Props {
  getInstitutions: GetEducationalInstitutionsAdapter
  patchInstitution: PatchEducationalInstitutionAdapter
  mode: Mode
}

const CollectiveOfferVisibility = ({
  getInstitutions,
  mode,
  patchInstitution,
}: Props) => {
  const formik = useFormik({
    initialValues: {
      visibility: 'all',
      institution: [],
      'search-institution': '',
    },
    onSubmit: () => {},
    validationSchema,
  })

  const notify = useNotification()
  const history = useHistory()

  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId, isShowcase } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)

  const [institutionsOptions, setInstitutionsOptions] =
    useState<SelectOption[]>()

  const [buttonPressed, setButtonPressed] = useState(false)

  const handleSubmit = () => {
    setButtonPressed(true)
    patchInstitution({
      offerId,
      institutionId: '12',
    }).then(result => {
      if (result.isOk) {
        notify.success(result.message)
        history.push(
          `/offre/${isShowcase ? 'T-' : ''}${offerId}/collectif/confirmation`
        )
      } else {
        notify.error(result.message)
        setButtonPressed(false)
      }
    })
  }

  useEffect(() => {
    if (formik.values.visibility === 'one' && !institutionsOptions) {
      getInstitutions().then(res => {
        if (res.isOk)
          setInstitutionsOptions(
            res.payload.institutions.map(({ name, id }) => ({
              label: name,
              value: id,
            }))
          )
      })
    }
  }, [formik.values.visibility])

  return (
    <FormikProvider value={formik}>
      <form
        onSubmit={() => {
          handleSubmit()
          formik.handleSubmit()
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
                <MultiSelectAutocomplete
                  fieldName="institution"
                  options={institutionsOptions}
                  label="Établissement scolaire"
                  maxDisplayOptions={20}
                  maxDisplayOptionsLabel="20 résultats maximum. Veuillez affiner votre recherche"
                  maxHeight={100}
                  pluralLabel="Établissements"
                  hideTags
                />
              </FormLayout.Row>
            )}
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
