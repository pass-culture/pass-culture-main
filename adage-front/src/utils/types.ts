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

export enum ADRESS_TYPE {
  OFFERER_VENUE = 'offererVenue',
  SCHOOL = 'school',
  OTHER = 'other',
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
  extraData?: {
    contactEmail?: string;
    contactPhone?: string;
    offerVenue?: {
      addressType: ADRESS_TYPE,
      otherAddress: string,
      venueId: string,
    }
    students?: string[];
  }
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
  numberOfTickets?: number;
}

// See attributesToRetrieve
export interface ResultType {
  objectID: string;
  offer: {
    dates: number[];
    name: string;
    thumbUrl: string;
  };
  venue: {
    name: string;
    publicName: string;
  };
}

export enum Role {
  redactor = "redactor",
  readonly = "readonly",
  unauthenticated = "unauthenticated",
}
