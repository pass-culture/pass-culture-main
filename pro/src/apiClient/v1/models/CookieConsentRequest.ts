/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Consent } from './Consent';

export type CookieConsentRequest = {
  choiceDatetime: string;
  consent: Consent;
  deviceId: string;
  userId?: number | null;
};

