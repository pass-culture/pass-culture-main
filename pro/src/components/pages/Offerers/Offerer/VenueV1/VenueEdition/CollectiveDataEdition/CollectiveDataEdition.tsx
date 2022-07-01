import { FormikProvider, useFormik } from 'formik'
import { MultiSelectAutocomplete, TextArea, TextInput, Title } from 'ui-kit'
import React, { useEffect, useState } from 'react'

import FormLayout from 'new_components/FormLayout'
import { SelectOption } from 'custom_types/form'
import { StudentLevels } from 'api/v1/gen'
import { getEducationalDomainsAdapter } from 'core/OfferEducational'
import styles from './CollectiveDataEdition.module.scss'
import useNotification from 'components/hooks/useNotification'
import { validationSchema } from './validationSchema'

type CollectiveDataFormValues = {
  collectiveDescription: string
  collectiveStudents: string[]
  collectiveWebsite: string
  collectivePhone: string
  collectiveEmail: string
  collectiveDomains: string[]
}

const initialValues: CollectiveDataFormValues = {
  collectiveDescription: '',
  collectiveStudents: [],
  collectiveWebsite: '',
  collectivePhone: '',
  collectiveEmail: '',
  collectiveDomains: [],
}

const studentOptions = [
  { value: StudentLevels.Collge4e, label: StudentLevels.Collge4e },
  { value: StudentLevels.Collge3e, label: StudentLevels.Collge3e },
  { value: StudentLevels.CAP1reAnne, label: StudentLevels.CAP1reAnne },
  { value: StudentLevels.CAP2eAnne, label: StudentLevels.CAP1reAnne },
  { value: StudentLevels.LyceSeconde, label: StudentLevels.LyceSeconde },
  { value: StudentLevels.LycePremire, label: StudentLevels.LycePremire },
  { value: StudentLevels.LyceTerminale, label: StudentLevels.LyceTerminale },
]

const CollectiveDataEdition = (): JSX.Element => {
  const notify = useNotification()

  const [domains, setDomains] = useState<SelectOption[]>([])

  const formik = useFormik<CollectiveDataFormValues>({
    initialValues,
    onSubmit: () => {},
    validationSchema,
  })

  useEffect(() => {
    getEducationalDomainsAdapter().then(response => {
      if (response.isOk) {
        setDomains(response.payload)
      } else {
        notify.error(response.message)
      }
    })
  }, [])

  return (
    <>
      <Title level={1}>Mes informations EAC</Title>
      <p className={styles.description}>
        Il s'agit d'un formulaire vous permettant de renseigner vos
        informattions EAC. Les informations renseignées seront visibles par les
        enseignants et chefs d'établissement sur Adage (Application Dédiée A la
        Généralisation de l'Education artistique et culturelle).
      </p>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <div className={styles.section}>
            Présentation de votre démarche EAC
          </div>
          <FormLayout.Row>
            <TextArea
              name="collectiveDescription"
              label="Ajoutez des informations complémentaires  concernant l’EAC."
              placeholder="Détaillez ici des informations complémentaires"
              maxLength={500}
              countCharacters
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <MultiSelectAutocomplete
              fieldName="collectiveStudents"
              label="Public cible :"
              options={studentOptions}
              placeholder="Sélectionner un public cible"
              inline
              className={styles.row}
              hideTags
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <TextInput
              name="collectiveWebsite"
              label="URL de votre site web :"
              placeholder="http://exemple.com"
              inline
              className={styles.row}
            />
          </FormLayout.Row>
          <div className={styles.section}>
            Informations du lieu relatives à l’EAC
          </div>
          <FormLayout.Row>
            <MultiSelectAutocomplete
              hideTags
              options={domains}
              fieldName="collectiveDomains"
              label="Domaine artistique et culturel :"
              placeholder="Sélectionner un ou plusieurs domaine(s)"
              className={styles.row}
              inline
            />
          </FormLayout.Row>
          <div className={styles.section}>Contact pour les scolaires</div>
          <FormLayout.Row>
            <TextInput
              name="collectivePhone"
              label="Téléphone :"
              placeholder="0648592819"
              inline
              className={styles.row}
            />
          </FormLayout.Row>
          <FormLayout.Row>
            <TextInput
              name="collectiveEmail"
              label="E-mail :"
              placeholder="email@exemple.com"
              inline
              className={styles.row}
            />
          </FormLayout.Row>
        </form>
      </FormikProvider>
    </>
  )
}

export default CollectiveDataEdition
