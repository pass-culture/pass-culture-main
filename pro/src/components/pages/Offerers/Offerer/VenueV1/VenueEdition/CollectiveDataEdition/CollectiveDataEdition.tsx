import { FormikProvider, useFormik } from 'formik'
import { MultiSelectAutocomplete, TextArea, TextInput, Title } from 'ui-kit'

import FormLayout from 'new_components/FormLayout'
import React from 'react'
import { StudentLevels } from 'api/v1/gen'
import styles from './CollectiveDataEdition.module.scss'

type CollectiveDataFormValues = {
  collectiveDescription: string
  collectiveStudents: string[]
  collectiveWebsite: string
}

const initialValues = {
  collectiveDescription: '',
  collectiveStudents: [],
  collectiveWebsite: '',
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
  const formik = useFormik<CollectiveDataFormValues>({
    initialValues,
    onSubmit: () => {},
  })

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
              pluralLabel="Public cible :"
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
        </form>
      </FormikProvider>
    </>
  )
}

export default CollectiveDataEdition
