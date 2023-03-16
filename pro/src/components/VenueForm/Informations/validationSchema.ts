import * as yup from 'yup'

const validationSchema = (newOnboardingActive?: boolean) => {
  const nameTitle = newOnboardingActive
    ? 'la raison sociale'
    : 'le nom juridique'
  return {
    name: yup
      .string()
      .required(`Veuillez renseigner ${nameTitle} de votre lieu`),
  }
}

export default validationSchema
