import { FormikProvider, useFormik } from 'formik'
import React, { useMemo, useState } from 'react'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  EducationalInstitutionResponseModel,
  EducationalRedactor,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { BannerPublicApi } from 'components/Banner/BannerPublicApi'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OfferEducationalActions } from 'components/OfferEducationalActions/OfferEducationalActions'
import { GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY } from 'config/swrQueryKeys'
import {
  VisibilityFormValues,
  isCollectiveOffer,
  Mode,
} from 'core/OfferEducational/types'
import {
  extractInitialVisibilityValues,
  formatInstitutionDisplayName,
} from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import {
  GET_DATA_ERROR_MESSAGE,
  SENT_DATA_ERROR_MESSAGE,
} from 'core/shared/constants'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import strokeSearch from 'icons/stroke-search.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import Spinner from 'ui-kit/Spinner/Spinner'
import {
  normalizeStrForSearch,
  searchPatternInOptions,
  SelectOptionNormalized,
} from 'utils/searchPatternInOptions'

import styles from './CollectiveOfferVisibility.module.scss'
import validationSchema from './validationSchema'

export interface CollectiveOfferVisibilityProps {
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
  offer: GetCollectiveOfferResponseModel
  requestId?: string | null
}
interface InstitutionOption extends SelectOptionNormalized {
  postalCode?: string
  city?: string
  name: string
  institutionType?: string
  institutionId: string
}

interface TeacherOption extends SelectOption {
  surname?: string | null
  name: string
  gender?: string | null
  email: string
}

export const CollectiveOfferVisibilityScreen = ({
  mode,
  initialValues,
  onSuccess,
  institutions,
  isLoadingInstitutions,
  offer,
  requestId = '',
}: CollectiveOfferVisibilityProps) => {
  const notify = useNotification()

  const [teachersOptions, setTeachersOptions] = useState<TeacherOption[]>([])
  const [buttonPressed, setButtonPressed] = useState(false)

  const institutionsOptions: InstitutionOption[] = useMemo(
    () =>
      institutions.map(
        ({ name, id, city, postalCode, institutionType, institutionId }) => {
          const label = formatInstitutionDisplayName({
            name,
            institutionType: institutionType || '',
            institutionId,
            city,
            postalCode,
          })
          return {
            label: label,
            normalizedLabel: normalizeStrForSearch(label),
            value: String(id),
            city,
            postalCode,
            name,
            institutionType: institutionType ?? '',
            institutionId: institutionId,
          }
        }
      ),
    [institutions]
  )

  const { data: requestInformations } = useSWR(
    () =>
      requestId
        ? [GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY, requestId]
        : null,
    ([, id]) => api.getCollectiveOfferRequest(Number(id))
  )

  const onSubmit = async (values: VisibilityFormValues) => {
    setButtonPressed(true)

    try {
      const collectiveOffer =
        await api.patchCollectiveOffersEducationalInstitution(offer.id, {
          educationalInstitutionId: Number(values.institution),
          teacherEmail: selectedTeacher ? selectedTeacher.email : null,
        })

      onSuccess({
        offerId: offer.id.toString(),
        message:
          'Les paramètres de visibilité de votre offre ont bien été enregistrés',
        payload: collectiveOffer,
      })

      formik.resetForm({
        values: extractInitialVisibilityValues(collectiveOffer.institution),
      })
      setButtonPressed(false)
    } catch {
      notify.error(SENT_DATA_ERROR_MESSAGE)
      setButtonPressed(false)
    }
  }

  initialValues = requestInformations
    ? {
        ...extractInitialVisibilityValues(null, null, requestInformations),
        institution:
          institutionsOptions
            .find(
              (option) =>
                option.institutionId ===
                requestInformations.institution.institutionId
            )
            ?.value.toString() || '',
      }
    : initialValues

  const formik = useFormik<VisibilityFormValues>({
    initialValues,
    onSubmit,
    validationSchema,
    enableReinitialize: true,
  })

  const selectedTeacher: TeacherOption | null = requestId
    ? teachersOptions[0]
    : teachersOptions.find(
        (teacher) => teacher.value === formik.values.teacher
      ) ?? null

  const selectedInstitution: InstitutionOption | null = requestId
    ? institutionsOptions.filter(({ label }) =>
        label
          .toLowerCase()
          .includes(formik.values['search-institution'].trim().toLowerCase())
      )[0]
    : institutionsOptions.find(
        (institution) => institution.value === formik.values.institution
      ) ?? null

  const onChangeTeacher = async () => {
    const searchTeacherValue = formik.values['search-teacher']?.trim()

    if (
      !searchTeacherValue ||
      searchTeacherValue.length < 3 ||
      !selectedInstitution
    ) {
      setTeachersOptions([])
      return
    }

    try {
      const payload = await api.getAutocompleteEducationalRedactorsForUai(
        selectedInstitution.institutionId,
        searchTeacherValue
      )
      setTeachersOptions(
        payload.map(
          ({
            name,
            surname,
            gender,
            email,
          }: EducationalRedactor): TeacherOption => ({
            label: `${surname} ${name}`.trim(),
            value: email,
            surname,
            name,
            gender,
            email,
          })
        )
      )
    } catch (e) {
      notify.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  return (
    <>
      <FormLayout.MandatoryInfo />

      <OfferEducationalActions
        className={styles.actions}
        isBooked={Boolean(offer.collectiveStock?.isBooked)}
        offer={offer}
        mode={mode}
      />

      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <FormLayout>
            {isCollectiveOffer(offer) && offer.isPublicApi && (
              <BannerPublicApi className={styles['banner-space']}>
                Offre importée automatiquement
              </BannerPublicApi>
            )}
            <FormLayout.Section title="Établissement scolaire et enseignant">
              <p className={styles['description-text']}>
                L’établissement et l’enseignant renseignés sont les seuls à
                pouvoir visualiser et préréserver votre offre sur ADAGE.
              </p>

              <FormLayout.Row className={styles['row-layout']}>
                {isLoadingInstitutions ? (
                  <Spinner />
                ) : (
                  <>
                    <SelectAutocomplete
                      name="institution"
                      type="search"
                      options={institutionsOptions}
                      label="Nom de l’établissement scolaire ou code UAI"
                      placeholder="Ex : Lycee General Simone Weil ou 010456E ou Le Havre"
                      hideArrow
                      onReset={async () => {
                        setTeachersOptions([])
                        await formik.setFieldValue('search-teacher', '')
                      }}
                      onSearch={async () => {
                        if (formik.dirty) {
                          await formik.setFieldValue('institution', '')
                          await formik.setFieldValue('search-teacher', '')
                        }
                      }}
                      resetOnOpen={false}
                      disabled={mode === Mode.READ_ONLY}
                      searchInOptions={(options, pattern) =>
                        searchPatternInOptions(options, pattern, 300)
                      }
                      leftIcon={strokeSearch}
                    />
                  </>
                )}
              </FormLayout.Row>

              <FormLayout.Row className={styles['row-layout']}>
                <SelectAutocomplete
                  name="teacher"
                  type="search"
                  options={teachersOptions}
                  label="Prénom et nom de l’enseignant (au moins 3 caractères)"
                  isOptional
                  placeholder="Ex: Camille Dupont"
                  hideArrow
                  disabled={mode === Mode.READ_ONLY || !selectedInstitution}
                  onSearch={async () => {
                    await onChangeTeacher()
                  }}
                  resetOnOpen={false}
                  leftIcon={strokeSearch}
                />
              </FormLayout.Row>
            </FormLayout.Section>
            <ActionsBarSticky>
              <ActionsBarSticky.Left>
                <ButtonLink
                  variant={ButtonVariant.SECONDARY}
                  link={{
                    to:
                      mode === Mode.CREATION
                        ? `/offre/${offer.id}/collectif/stocks${
                            requestId ? `?requete=${requestId}` : ''
                          }`
                        : '/offres/collectives',
                    isExternal: false,
                  }}
                >
                  {mode === Mode.CREATION
                    ? 'Étape précédente'
                    : 'Annuler et quitter'}
                </ButtonLink>
                <Button
                  type="submit"
                  disabled={
                    buttonPressed ||
                    !formik.values.institution ||
                    mode === Mode.READ_ONLY
                  }
                  isLoading={false}
                >
                  {mode === Mode.CREATION
                    ? 'Étape suivante'
                    : 'Enregistrer les modifications'}
                </Button>
              </ActionsBarSticky.Left>
            </ActionsBarSticky>
          </FormLayout>
        </form>
      </FormikProvider>
    </>
  )
}
