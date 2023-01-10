export const SIGNUP_FORM_DEFAULT_VALUES = {
  email: '',
  password: '',
  lastName: '',
  firstName: '',
  phoneNumber: '',
  contactOk: false,
  siren: '',
  legalUnitValues: {
    address: '',
    city: '',
    name: '',
    postalCode: '',
    siren: '',
  },
}

// APE/NAF codes for :
//   - Enseignement secondaire général (85.31Z)
//   - Enseignement secondaire technique ou professionnel (85.32Z)
export const MAYBE_APP_USER_APE_CODE = ['85.31Z', '85.32Z']
