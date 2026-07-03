import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect, useMemo, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import useSWR, { useSWRConfig } from 'swr'
import { useDebouncedCallback } from 'use-debounce'

import { api } from '@/apiClient/api'
import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import {
  CollectiveOfferAllowedAction,
  type EducationalInstitutionResponseModel,
  type EducationalRedactor,
  type GetCollectiveOfferResponseModel,
  type PatchCollectiveOfferEducationalInstitution,
} from '@/apiClient/v1'
import {
  GET_AUTOCOMPLETE_EDUCATIONAL_REDACTORS_FOR_UAI_KEY,
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { isCollectiveOffer, Mode } from '@/commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import {
  extractInitialInstitutionValues,
  formatInstitutionDisplayName,
} from '@/commons/core/OfferEducational/utils/extractInitialInstitutionValues'
import {
  GET_DATA_ERROR_MESSAGE,
  SENT_DATA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import type { SelectOption } from '@/commons/custom_types/form'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { searchPatternInOptions } from '@/commons/utils/searchPatternInOptions'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { BannerPublicApi } from '@/components/BannerPublicApi/BannerPublicApi'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OfferEducationalActions } from '@/components/OfferEducationalActions/OfferEducationalActions'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SelectAutocomplete } from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import {
  GET_REDACTOR_NOT_FOUND_ERROR_MESSAGE,
  INSTITUTION_GENERIC_ERROR_MESSAGE,
  REDACTOR_GENERIC_ERROR_MESSAGE,
} from '../../commons/constants'
import {
  type InstitutionFormValues,
  validationSchema,
} from '../../commons/validationSchema'
import styles from './CollectiveOfferInstitution.module.scss'

export interface CollectiveOfferInstitutionProps {
  mode: Mode
  initialValues: InstitutionFormValues
  institutions: EducationalInstitutionResponseModel[]
  isLoadingInstitutions: boolean
  offer: GetCollectiveOfferResponseModel
  requestId?: string | null
}
interface InstitutionOption extends SelectOption {
  institutionId: string
}

interface TeacherOption extends SelectOption {
  surname: string | null
  name: string
  email: string
}

export const CollectiveOfferInstitutionScreen = ({
  mode,
  initialValues,
  institutions,
  isLoadingInstitutions,
  offer,
  requestId = '',
}: CollectiveOfferInstitutionProps) => {
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  const snackBar = useSnackBar()
  const { mutate } = useSWRConfig()

  const [teachersOptions, setTeachersOptions] = useState<TeacherOption[]>([])

  const canEditInstitution = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION
  )

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
            label,
            value: String(id),
            institutionId,
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
    ([, id]) =>
      api.getCollectiveOfferRequest({ path: { request_id: Number(id) } })
  )

  const manualFormValidation = (
    body: PatchCollectiveOfferEducationalInstitution
  ) => {
    if (!body.educationalInstitutionId) {
      form.setError('educationalInstitution', {
        message: INSTITUTION_GENERIC_ERROR_MESSAGE,
      })
      return false
    }
    if (watch('teacherEmail') && !body.teacherEmail) {
      form.setError('teacherEmail', {
        message: REDACTOR_GENERIC_ERROR_MESSAGE,
      })
      return false
    }
    return true
  }

  const onSubmit = async (values: InstitutionFormValues): Promise<boolean> => {
    if (!form.formState.isDirty && !requestId) {
      return true
    }

    const selectedTeacher: TeacherOption | null = requestId
      ? teachersOptions[0]
      : (teachersOptions.find(
          (teacher) => teacher.value === watch('teacherEmail')
        ) ?? null)
    const teacherEmail = selectedTeacher ? selectedTeacher.email : null

    const isValid = manualFormValidation({
      educationalInstitutionId: Number(values.educationalInstitution),
      teacherEmail,
    })
    if (!isValid) {
      return false
    }

    try {
      const collectiveOffer =
        await api.patchCollectiveOffersEducationalInstitution({
          path: { offer_id: offer.id },
          body: {
            educationalInstitutionId: Number(values.educationalInstitution),
            teacherEmail,
          },
        })
      await mutate(
        [GET_COLLECTIVE_OFFER_QUERY_KEY, Number(offer.id)],
        collectiveOffer,
        { revalidate: false }
      )

      reset({
        ...extractInitialInstitutionValues(collectiveOffer.institution),
      })

      snackBar.success(
        'Les paramètres de visibilité de votre offre ont bien été enregistrés'
      )

      return true
    } catch (error) {
      if (isErrorAPIError(error)) {
        serializeApiErrors(error.body, form.setError)
      } else {
        snackBar.error(SENT_DATA_ERROR_MESSAGE)
      }

      return false
    }
  }

  initialValues = requestInformations
    ? {
        ...extractInitialInstitutionValues(null, null, requestInformations),
        educationalInstitution:
          institutionsOptions
            .find(
              (option) =>
                option.institutionId ===
                requestInformations.institution.institutionId
            )
            ?.value.toString() || '',
      }
    : initialValues

  const form = useForm<InstitutionFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver<InstitutionFormValues, unknown, unknown>(
      validationSchema
    ),
    mode: 'onBlur',
  })

  const {
    setValue,
    reset,
    watch,
    formState: { isDirty, errors },
  } = form

  const afterSubmitPath =
    mode === Mode.CREATION
      ? `/offre/${offer.id}/collectif/creation/recapitulatif`
      : `/offre/${computeURLCollectiveOfferId(
          offer.id,
          false
        )}/collectif/recapitulatif`
  const { navigationGuardDialog, navigationGuardedSubmitHandler } =
    useFormNavigationGuard({ afterSubmitPath, form, onSubmit })

  const institution = watch('educationalInstitution')
  const selectedInstitution = institutionsOptions.find(
    (_institution) => _institution.value === institution
  )

  const teacherEmail = watch('teacherEmail')
  const selectedTeacher = teachersOptions.find(
    (_teacher) => _teacher.value === teacherEmail
  )

  const { isLoading: isPreloadingRedactors } = useSWR(
    () =>
      selectedInstitution?.institutionId
        ? [
            GET_AUTOCOMPLETE_EDUCATIONAL_REDACTORS_FOR_UAI_KEY,
            selectedInstitution?.institutionId,
          ]
        : null,
    async ([, institutionUai]) => {
      try {
        if (institutionUai) {
          await api.getAutocompleteEducationalRedactorsForUai({
            query: { uai: institutionUai, candidate: 'preload' },
          })
        }
      } catch (error) {
        if (isErrorAPIError(error) && error.status === 404) {
          console.warn('No redactors found')
        } else {
          snackBar.error(GET_DATA_ERROR_MESSAGE)
        }
      }
    }
  )

  useEffect(() => {
    if (!requestInformations) {
      return
    }

    const institutionOption = institutionsOptions.find(
      (opt) =>
        opt.institutionId === requestInformations.institution.institutionId
    )

    const formValues: InstitutionFormValues = {
      ...extractInitialInstitutionValues(null, null, requestInformations),
      educationalInstitution: institutionOption?.value.toString() ?? '',
      teacherEmail: requestInformations.redactor.email,
    }

    reset(formValues)

    const { firstName, lastName, email } = requestInformations.redactor
    setTeachersOptions([
      {
        label: `${firstName ?? ''} ${lastName ?? ''}`.trim(),
        value: email,
        surname: lastName ?? '',
        name: firstName ?? '',
        email,
      },
    ])
  }, [requestInformations, institutionsOptions, reset])

  const onSearchTeacher = useDebouncedCallback(async (pattern: string) => {
    const selectedInstitution = institutionsOptions.find(
      (institution) => institution.value === watch('educationalInstitution')
    )

    const searchTeacherValue = pattern.trim()

    if (
      !searchTeacherValue ||
      searchTeacherValue.length < 3 ||
      !selectedInstitution
    ) {
      setTeachersOptions([])
      return
    }

    try {
      const payload = await api.getAutocompleteEducationalRedactorsForUai({
        query: {
          uai: selectedInstitution.institutionId,
          candidate: searchTeacherValue,
        },
      })
      setTeachersOptions(
        payload.map(
          ({ name, surname, email }: EducationalRedactor): TeacherOption => ({
            label: `${surname} ${name}`.trim(),
            value: email,
            surname,
            name,
            email,
          })
        )
      )
    } catch {
      form.setError('teacherEmail', {
        message: GET_REDACTOR_NOT_FOUND_ERROR_MESSAGE,
      })
    }
  }, 400)

  const requestIdQueryParam = requestId ? `?requete=${requestId}` : ''
  const previousStepPath = isNewCollectivePriceEnabled
    ? `/offre/${offer.id}/collectif/informations-pratiques${requestIdQueryParam}`
    : `/offre/${offer.id}/collectif/stocks${requestIdQueryParam}`

  return (
    <>
      <OfferEducationalActions
        className={styles.actions}
        offer={offer}
        mode={mode}
      />

      <FormProvider {...form}>
        <div className={styles.container}>
          <form onSubmit={navigationGuardedSubmitHandler}>
            <FormLayout>
              {isCollectiveOffer(offer) && offer.isPublicApi && (
                <BannerPublicApi className={styles['banner-space']} />
              )}
              <FormLayout.Section title="Renseignez l'établissement scolaire et l'enseignant">
                <p className={styles['description-text']}>
                  L’établissement et l’enseignant renseignés sont les seuls à
                  pouvoir visualiser et préréserver votre offre sur ADAGE.
                </p>
                <FormLayout.Row className={styles['row-layout']} mdSpaceAfter>
                  {isLoadingInstitutions ? (
                    <Spinner />
                  ) : (
                    <SelectAutocomplete
                      name="institution"
                      options={institutionsOptions}
                      label="Nom de l’établissement scolaire ou code UAI"
                      description="Ex : Lycee General Simone Weil ou 010456E ou Le Havre"
                      shouldResetOnOpen={true}
                      onSearch={(searchText) => {
                        setValue('educationalInstitution', searchText, {
                          shouldDirty: true,
                          shouldValidate: true,
                        })
                      }}
                      onChange={(event) => {
                        setValue('educationalInstitution', event.target.value, {
                          shouldDirty: true,
                          shouldValidate: true,
                        })

                        setValue('teacherEmail', '')
                        setValue('teacherName', '')
                      }}
                      disabled={!canEditInstitution}
                      searchInOptions={(options, pattern) =>
                        searchPatternInOptions(options, pattern, 300)
                      }
                      value={selectedInstitution?.value ?? ''}
                      error={errors.educationalInstitution?.message}
                      required
                      requiredIndicator="explicit"
                    />
                  )}
                </FormLayout.Row>
                <FormLayout.Row className={styles['row-layout']}>
                  <SelectAutocomplete
                    name="teacherEmail"
                    options={teachersOptions}
                    label="Prénom et nom de l’enseignant (au moins 3 caractères)"
                    required={false}
                    description="Ex: Camille Dupont"
                    shouldResetOnOpen={true}
                    onSearch={(searchText) => {
                      setValue('teacherEmail', searchText, {
                        shouldDirty: true,
                        shouldValidate: true,
                      })
                      onSearchTeacher(searchText)
                    }}
                    disabled={
                      !canEditInstitution ||
                      !watch('educationalInstitution') ||
                      isPreloadingRedactors
                    }
                    onChange={(event) => {
                      setValue('teacherEmail', event.target.value, {
                        shouldDirty: true,
                        shouldValidate: true,
                      })
                    }}
                    value={selectedTeacher?.value || watch('teacherName')}
                    error={errors.teacherEmail?.message}
                  />
                </FormLayout.Row>
              </FormLayout.Section>
              <ActionsBarSticky>
                <ActionsBarSticky.Left>
                  <Button
                    as="a"
                    variant={ButtonVariant.SECONDARY}
                    color={
                      mode === Mode.CREATION
                        ? ButtonColor.BRAND
                        : ButtonColor.NEUTRAL
                    }
                    to={
                      mode === Mode.CREATION
                        ? previousStepPath
                        : '/offres/collectives'
                    }
                    label={
                      mode === Mode.CREATION ? 'Retour' : 'Annuler et quitter'
                    }
                  />
                </ActionsBarSticky.Left>
                <ActionsBarSticky.Right dirtyForm={isDirty} mode={mode}>
                  <Button
                    type="submit"
                    disabled={
                      !watch('educationalInstitution') || !canEditInstitution
                    }
                    label="Enregistrer et continuer"
                  />
                </ActionsBarSticky.Right>
              </ActionsBarSticky>
            </FormLayout>
          </form>
        </div>
      </FormProvider>

      {navigationGuardDialog}
    </>
  )
}
