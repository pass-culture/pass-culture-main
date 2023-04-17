/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Model of a validation error response element.
 */
export type ValidationErrorElement = {
  ctx?: Record<string, any>;
  loc: Array<string>;
  msg: string;
  type: string;
};

