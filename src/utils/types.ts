export interface VenueType {
  address: string;
  city: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  name: string;
  postalCode: string;
  publicName?: string;
}

export interface OfferType {
  id: number;
  name: string;
  subcategoryLabel: string;
  description: string;
  venue: VenueType;
  stocks: StockType[];
  isSoldOut: boolean;
  isExpired: boolean;
}

export interface VenueFilterType {
  id: number;
  name: string;
  publicName?: string;
}

export interface StockType {
  id: number;
  beginningDatetime: Date;
  isBookable: boolean;
  price: number;
}

export interface ResultType {
  dates: { raw: string[] | null };
  id: { raw: string };
  name: { raw: string };
  thumb_url: { raw: string | null };
  venue_name: { raw: string | null };
  venue_public_name: { raw: string | null };
}

export enum Role {
  redactor = "redactor",
  readonly = "readonly",
  unauthenticated = "unauthenticated",
}
