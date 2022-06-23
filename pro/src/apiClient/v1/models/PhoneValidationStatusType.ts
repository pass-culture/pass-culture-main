/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * An enumeration.
 */
export enum PhoneValidationStatusType {
  BLOCKED_TOO_MANY_CODE_SENDINGS = 'blocked-too-many-code-sendings',
  BLOCKED_TOO_MANY_CODE_VERIFICATION_TRIES = 'blocked-too-many-code-verification-tries',
  SKIPPED_BY_SUPPORT = 'skipped-by-support',
  UNVALIDATED = 'unvalidated',
  VALIDATED = 'validated',
}
