import Offers from './Offers'

export default class OffersWithCover extends Offers {
  constructor({ algolia = {}, cover = '', display = {}, moduleId = '' }) {
    super({ algolia, display, moduleId })
    this.cover = cover
  }
}
