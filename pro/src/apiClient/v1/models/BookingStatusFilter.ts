/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * An enumeration.
 */
export enum BookingStatusFilter {
  BOOKED = 'booked',
  VALIDATED = 'validated',
  REIMBURSED = 'reimbursed',
}

export function isBookingStatusFilter(
  value: any
): value is BookingStatusFilter {
  return Object.values(BookingStatusFilter).includes(value)
}
