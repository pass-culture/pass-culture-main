import Offers from './Offers'

export default class OffersWithCover extends Offers {
  constructor({ algolia = {}, cover = '', display = {} }) {
    super({algolia, display})
    this.cover = cover
  }
}
