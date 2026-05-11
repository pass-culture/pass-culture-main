/*
  Key names match the new <RegistrationStepper /> step titles,
  but the values try to remain consistent with the old <SignupJourneyStepper /> constants for backward compatibility with Data team

  TODO (jclery, 2026-04-30): Check with Data team to uniformize values
*/

export enum REGISTRATION_STEP_IDS {
  SIGNUP = 'creation',
  SIRET = 'structure',
  STRUCTURE = 'identification',
  ACTIVITY = 'activite',
  VALIDATION = 'confirmation',
  COMPLETED = 'completed',
}
