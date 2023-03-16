import * as yup from 'yup'

const validationSchema = (newOnboardingActive?: boolean) => {
  return {
    venueType: yup
      .string()
      .required(
        `Veuillez sélectionner ${
          newOnboardingActive ? 'une activité principale' : 'un type de lieu'
        }`
      ),
  }
}

export default validationSchema
