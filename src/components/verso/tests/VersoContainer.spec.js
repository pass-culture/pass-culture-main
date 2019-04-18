/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
// $(yarn bin)/jest --env=jsdom ./src/components/verso/tests/VersoContainer.spec.js --watch
import set from 'lodash.set';

import { ROOT_PATH } from '../../../utils/config';
import {
  checkIsTuto,
  getBackgroundColor,
  getContentInlineStyle,
  getOfferVenue,
  getOfferName,
} from '../VersoContainer';

const backgroundColor = 'hsl(355, 100%, 7.5%)';
const firstThumbDominantColor = [224, 108, 117];
const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`;

let result;
let isTuto;
let expected;
let recommendation = {};
const name = 'Offer title';

describe('src | components | verso | VersoContainer', () => {
  describe('getContentInlineStyle', () => {
    it('returns only backgroundImage', () => {
      // given
      isTuto = false;
      // when
      result = getContentInlineStyle(isTuto, backgroundColor);
      // then
      expected = { backgroundImage };
      expect(result).toStrictEqual(expected);
    });

    it('returns backgroundImage and backgroundColor', () => {
      // given
      isTuto = true;
      // when
      result = getContentInlineStyle(isTuto, backgroundColor);
      // then
      expected = { backgroundColor, backgroundImage };
      expect(result).toStrictEqual(expected);
    });
  });

  describe('checkIsTuto', () => {
    it('returns true', () => {
      // given
      recommendation = {};
      set(recommendation, 'mediation.tutoIndex', 42);
      // when
      result = checkIsTuto(recommendation);
      // then
      expected = true;
      expect(result).toEqual(expected);
    });

    it('returns false', () => {
      expected = false;
      // given
      recommendation = {};
      set(recommendation, 'mediation.tutoIndex', null);
      // when
      result = checkIsTuto(recommendation);
      // thens
      expect(result).toEqual(expected);

      // given
      recommendation = {};
      set(recommendation, 'mediation', null);
      // when
      result = checkIsTuto(recommendation);
      // then
      expect(result).toEqual(expected);
    });
  });

  describe('getOfferVenue', () => {
    it('returns a string value', () => {
      // given
      recommendation = {};
      set(recommendation, 'offer.venue.name', name);
      // when
      result = getOfferVenue(recommendation);
      // then
      expected = 'Offer title';
      expect(result).toEqual(expected);
    });

    it('returns null', () => {
      // given
      recommendation = {};
      set(recommendation, 'offer.venue');
      // when
      result = getOfferVenue(recommendation);
      // then
      expected = null;
      expect(result).toEqual(expected);
    });
  });

  describe('getOfferName', () => {
    it('returns a string value', () => {
      // given
      recommendation = {};
      set(recommendation, 'offer.name', name);
      // when
      result = getOfferName(recommendation);
      // then
      expected = name;
      expect(result).toEqual(expected);
    });

    it('returns null', () => {
      // given
      recommendation = {};
      set(recommendation, 'offer.name', null);
      // when
      result = getOfferName(recommendation);
      // then
      expected = null;
      expect(result).toEqual(expected);
    });
  });

  describe('getBackgroundColor', () => {
    it('returns a string value', () => {
      // givent
      recommendation = {};
      set(recommendation, 'firstThumbDominantColor', firstThumbDominantColor);
      // then
      result = getBackgroundColor(recommendation);
      // then
      expect(result).toEqual(backgroundColor);
    });
  });
});
