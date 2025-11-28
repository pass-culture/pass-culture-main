/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AdagePlaylistType } from './AdagePlaylistType';
export type PlaylistBody = {
  domainId?: number | null;
  iframeFrom: string;
  index?: number | null;
  isFromNoResult?: boolean | null;
  numberOfTiles?: number | null;
  offerId?: number | null;
  playlistId: number;
  playlistType: AdagePlaylistType;
  queryId?: string | null;
  venueId?: number | null;
};

