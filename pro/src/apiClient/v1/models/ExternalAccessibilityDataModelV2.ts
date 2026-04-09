/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AudioDisabilityModelV2 } from './AudioDisabilityModelV2';
import type { MentalDisabilityModelV2 } from './MentalDisabilityModelV2';
import type { MotorDisabilityModelV2 } from './MotorDisabilityModelV2';
import type { VisualDisabilityModelV2 } from './VisualDisabilityModelV2';
export type ExternalAccessibilityDataModelV2 = {
  audioDisability?: AudioDisabilityModelV2;
  isAccessibleAudioDisability?: boolean;
  isAccessibleMentalDisability?: boolean;
  isAccessibleMotorDisability?: boolean;
  isAccessibleVisualDisability?: boolean;
  mentalDisability?: MentalDisabilityModelV2;
  motorDisability?: MotorDisabilityModelV2;
  visualDisability?: VisualDisabilityModelV2;
};

