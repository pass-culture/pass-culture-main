import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'

import {
  EducationalInstitutionResponseModel,
  EducationalRedactor,
  GetCollectiveOfferRequestResponseModel,
} from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import BannerPublicApi from 'components/Banner/BannerPublicApi'
import FormLayout from 'components/FormLayout'
import OfferEducationalActions from 'components/OfferEducationalActions'
import {
  CollectiveOffer,
  isCollectiveOffer,
  Mode,
  VisibilityFormValues,
} from 'core/OfferEducational'
import {
  extractInitialVisibilityValues,
  formatInstitutionDisplayName,
} from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import getOfferRequestInformationsAdapter from 'pages/CollectiveOfferFromRequest/adapters/getOfferRequestInformationsAdapter'
import { PatchEducationalInstitutionAdapter } from 'pages/CollectiveOfferVisibility/adapters/patchEducationalInstitutionAdapter'
import { ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import SelectAutocomplete from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import Spinner from 'ui-kit/Spinner/Spinner'
import { searchPatternInOptions } from 'utils/searchPatternInOptions'

import getEducationalRedactorsAdapter from './adapters/getEducationalRedactorAdapter'
import styles from './CollectiveOfferVisibility.module.scss'
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
    payload: CollectiveOffer
  }) => void
  institutions: EducationalInstitutionResponseModel[]
  isLoadingInstitutions: boolean
  offer: CollectiveOffer
  reloadCollectiveOffer?: () => void
  requestId?: string | null
}
interface InstitutionOption extends SelectOption {
  postalCode?: string
  city?: string
  name: string
  institutionType?: string
  institutionId: string
}

interface TeacherOption extends SelectOption {
  surname: string
  name: string
  gender: string
  email: string
}

const CollectiveOfferVisibility = ({
  mode,
  patchInstitution,
  initialValues,
  onSuccess,
  institutions,
  isLoadingInstitutions,
  offer,
  reloadCollectiveOffer,
  requestId = '',
}: CollectiveOfferVisibilityProps) => {
  const notify = useNotification()

  const [teachersOptions, setTeachersOptions] = useState<TeacherOption[]>([])
  const [buttonPressed, setButtonPressed] = useState(false)
  const [requestInformations, setRequestInformations] =
    useState<GetCollectiveOfferRequestResponseModel | null>(null)

  const institutionsOptions: InstitutionOption[] = institutions.map(
    ({ name, id, city, postalCode, institutionType, institutionId }) => ({
      label: formatInstitutionDisplayName({
        name,
        institutionType: institutionType || '',
        institutionId,
        city,
        postalCode,
      }),
      value: String(id),
      city,
      postalCode,
      name,
      institutionType: institutionType ?? '',
      institutionId: institutionId,
    })
  )

  const getOfferRequestInformation = async () => {
    const { isOk, message, payload } = await getOfferRequestInformationsAdapter(
      Number(requestId)
    )

    if (!isOk) {
      return notify.error(message)
    }

    setRequestInformations(payload)
  }

  useEffect(() => {
    requestId && getOfferRequestInformation()
  }, [])

  const onSubmit = async (values: VisibilityFormValues) => {
    setButtonPressed(true)
    const result = await patchInstitution({
      offerId: offer.id,
      institutionId: values.institution,
      teacherEmail: selectedTeacher ? selectedTeacher.email : null,
    })
    if (!result.isOk) {
      setButtonPressed(false)
      return notify.error(result.message)
    }
    onSuccess({
      offerId: offer.id.toString(),
      message: result.message ?? '',
      payload: result.payload,
    })
    setButtonPressed(false)
    formik.resetForm({
      values: extractInitialVisibilityValues(result.payload.institution),
    })
  }

  initialValues = requestInformations
    ? {
        ...extractInitialVisibilityValues(null, null, requestInformations),
        institution:
          institutionsOptions
            .find(
              option =>
                option.institutionId ==
                requestInformations?.institution.institutionId
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
    : teachersOptions?.find(
        teacher => teacher.value === formik.values.teacher
      ) ?? null

  const selectedInstitution: InstitutionOption | null = requestId
    ? institutionsOptions.filter(({ label }) =>
        label
          .toLowerCase()
          .includes(formik.values['search-institution'].trim().toLowerCase())
      )[0]
    : institutionsOptions?.find(
        institution => institution?.value === formik.values.institution
      ) ?? null

  const onChangeTeacher = async () => {
    const searchTeacherValue = formik.values['search-teacher']?.trim()

    if (
      !searchTeacherValue ||
      searchTeacherValue.length < 3 ||
      !selectedInstitution
    ) {
      return
    }
    const { payload } = await getEducationalRedactorsAdapter({
      uai: selectedInstitution?.institutionId,
      candidate: searchTeacherValue,
    })
    payload &&
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
  }

  return (
    <>
      <FormLayout.MandatoryInfo />
      <OfferEducationalActions
        reloadCollectiveOffer={reloadCollectiveOffer}
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
                L’établissement scolaire et l’enseignant renseignés seront les
                seuls à pouvoir visualiser et préréserver votre offre sur ADAGE.
              </p>
              {institutionsOptions && (
                <FormLayout.Row className={styles['row-layout']}>
                  {isLoadingInstitutions ? (
                    <Spinner />
                  ) : (
                    <>
                      <SelectAutocomplete
                        name="institution"
                        type="search"
                        options={institutionsOptions}
                        label="Nom de l'établissement scolaire ou code UAI"
                        placeholder="Ex : Lycee General Simone Weil ou 010456E ou Le Havre"
                        hideArrow
                        onReset={() => {
                          setTeachersOptions([])
                          formik.setFieldValue('search-teacher', '')
                        }}
                        disabled={mode === Mode.READ_ONLY}
                        searchInOptions={(options, pattern) =>
                          searchPatternInOptions(options, pattern, 300)
                        }
                      />
                    </>
                  )}
                </FormLayout.Row>
              )}
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
                  onSearch={() => {
                    onChangeTeacher()
                  }}
                />
              </FormLayout.Row>
            </FormLayout.Section>
            <ActionsBarSticky>
              <ActionsBarSticky.Left>
                <ButtonLink
                  variant={ButtonVariant.SECONDARY}
                  link={{
                    to: `/offre/${offer.id}/collectif/stocks${
                      requestId ? `?requete=${requestId}` : ''
                    }`,
                    isExternal: false,
                  }}
                >
                  Étape précédente
                </ButtonLink>
              </ActionsBarSticky.Left>
              <ActionsBarSticky.Right>
                <SubmitButton
                  disabled={
                    buttonPressed ||
                    !formik.values.institution ||
                    mode === Mode.READ_ONLY
                  }
                  isLoading={false}
                >
                  {mode === Mode.CREATION
                    ? 'Étape suivante'
                    : 'Valider et enregistrer l’offre'}
                </SubmitButton>
              </ActionsBarSticky.Right>
            </ActionsBarSticky>
          </FormLayout>
        </form>
      </FormikProvider>
    </>
  )
}

export default CollectiveOfferVisibility
