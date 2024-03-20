/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SuggestionType } from './SuggestionType';
export type TrackingAutocompleteSuggestionBody = {
  iframeFrom: string;
  isFromNoResult?: boolean | null;
  queryId?: string | null;
  suggestionType: SuggestionType;
  suggestionValue: string;
};

