export interface VenueType {
  address: string;
  city: string;
  latitude: string;
  longitude: string;
  name: string;
  postalCode: string;
  publicName: string;
}

export interface OfferType {
  venue: VenueType;
  stocks: StockType[];
}

export interface StockType {
  id: number;
  beginningDatetime: Date;
  bookingLimitDatetime: Date;
  isBookable: boolean;
  isExpired: boolean;
  isSoldOut: boolean;
  price: number;
}

export interface ResultType {
  dates: { raw: string | null };
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
