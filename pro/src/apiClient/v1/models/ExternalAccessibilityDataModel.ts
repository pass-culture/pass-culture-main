/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AudioDisabilityModel } from './AudioDisabilityModel';
import type { MentalDisabilityModel } from './MentalDisabilityModel';
import type { MotorDisabilityModel } from './MotorDisabilityModel';
import type { VisualDisabilityModel } from './VisualDisabilityModel';
export type ExternalAccessibilityDataModel = {
  audioDisability?: AudioDisabilityModel;
  isAccessibleAudioDisability?: boolean;
  isAccessibleMentalDisability?: boolean;
  isAccessibleMotorDisability?: boolean;
  isAccessibleVisualDisability?: boolean;
  mentalDisability?: MentalDisabilityModel;
  motorDisability?: MotorDisabilityModel;
  visualDisability?: VisualDisabilityModel;
};

