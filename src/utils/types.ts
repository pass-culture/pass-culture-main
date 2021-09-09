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
}

export interface ResultType {
  dates: { raw: string | null };
  id: { raw: string };
  name: { raw: string };
  thumb_url: { raw: string | null };
  venue_name: { raw: string | null };
  venue_public_name: { raw: string | null };
}
