import { createClient } from 'contentful'
import { fetchHomepage } from '../contentful'
import BusinessPane from '../../../components/pages/home/domain/ValueObjects/BusinessPane'
import { CONTENT_TYPES } from '../constants'
import { PANE_LAYOUT } from '../../../components/pages/home/domain/layout'
import Offers from '../../../components/pages/home/domain/ValueObjects/Offers'
import OffersWithCover from '../../../components/pages/home/domain/ValueObjects/OffersWithCover'
import ExclusivityPane from '../../../components/pages/home/domain/ValueObjects/ExclusivityPane'
import {
  CONTENTFUL_ACCESS_TOKEN,
  CONTENTFUL_ENVIRONMENT,
  CONTENTFUL_PREVIEW_TOKEN,
  CONTENTFUL_SPACE_ID,
} from '../../../utils/config'

jest.mock('contentful', () => ({
  createClient: jest.fn(),
}))
describe('src | vendor | contentful', () => {
  describe('error cases', () => {
    it('should throw an error when fetching data failed', async () => {
      // given
      const error = new Error('Something went wrong with the service')
      createClient.mockReturnValue({
        getEntries: jest.fn().mockRejectedValue(error),
      })

      // when/then
      await expect(fetchHomepage()).rejects.toThrow(error)
    })

    it('should throw an error when entry id is provided but fetch failed', async () => {
      // given
      const error = new Error('Something went wrong with the service')
      const mockGetEntry = jest.fn().mockRejectedValue(error)
      createClient.mockReturnValue({
        getEntry: mockGetEntry,
      })
      const entryId = 'ABCDE'

      // when/then
      await expect(fetchHomepage({ entryId: entryId })).rejects.toThrow(error)
    })

    it('should return throw an error when fields of module are empty', async () => {
      // given
      const module = {
        fields: {},
      }
      const error = new Error("Something went wrong with the service")
      createClient.mockReturnValue({
        getEntries: jest.fn().mockResolvedValue({
          items: [module],
        }),
      })

      // when / then
      await expect(fetchHomepage()).rejects.toThrow(error)
    })

    it('should return an empty array when fields of module "algoliaParameters" are empty', async () => {
      // given
      const module = {
        fields: {
          modules: [
            {
              fields: {
                algoliaParameters: {},
                displayParameters: {
                  fields: {
                    layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
                  },
                },
              },
              sys: {
                contentType: {
                  sys: { id: CONTENT_TYPES.ALGOLIA },
                },
              },
            },
          ],
        },
      }
      const error = new Error("Something went wrong with the service")
      createClient.mockReturnValue({
        getEntries: jest.fn().mockResolvedValue({
          items: [module],
        }),
      })

      // when /then
      await expect(fetchHomepage()).rejects.toThrow(error)
    })
  })

  it('should retrieve entries with the right parameters', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              image: {
                fields: {
                  file: {
                    url: '//my-image-url',
                  },
                },
              },
              title: 'my-title',
              url: 'my-url',
            },
            sys: {
              contentType: {
                sys: { id: 'not an algolia module' },
              },
            },
          },
        ],
      },
    }
    const mockGetEntries = jest.fn().mockResolvedValue({
      items: [module],
    })
    createClient.mockReturnValue({
      getEntries: mockGetEntries,
    })

    // when
    await fetchHomepage()

    // then
    expect(mockGetEntries).toHaveBeenCalledWith({ content_type: CONTENT_TYPES.HOMEPAGE, include: 2 })
  })

  it('should return a module for BusinessPane when not an algolia module', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              image: {
                fields: {
                  file: {
                    url: '//my-image-url',
                  },
                },
              },
              firstLine: 'my first line',
              secondLine: 'my second line',
              url: 'my-url',
            },
            sys: {
              contentType: {
                sys: { id: 'not an algolia module' },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    const business = new BusinessPane({
        firstLine: 'my first line',
        image: 'https://my-image-url',
        secondLine: 'my second line',
        url: 'my-url',
      },
    )
    expect(modules).toStrictEqual([business])
  })

  it('should return a module for Offers when an algolia module without cover', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              algoliaParameters: {
                fields: {
                  isDuo: true,
                },
              },
              displayParameters: {
                fields: {
                  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
                },
              },
            },
            sys: {
              contentType: {
                sys: { id: CONTENT_TYPES.ALGOLIA },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    const informationPane = new Offers({
        algolia: { isDuo: true },
        display: { layout: 'one-item-medium' },
      },
    )
    expect(modules).toStrictEqual([informationPane])
  })

  it('should return a module for OffersWithCover when an algolia module with cover', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              algoliaParameters: {
                fields: {
                  isDuo: true,
                },
              },
              cover: {
                fields: {
                  image: {
                    fields: {
                      file: {
                        url: '//my-cover-url',
                      },
                    },
                  },
                },
              },
              displayParameters: {
                fields: {
                  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
                },
              },
            },
            sys: {
              contentType: {
                sys: { id: CONTENT_TYPES.ALGOLIA },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    const offersWithCover = new OffersWithCover({
        algolia: { isDuo: true },
        cover: 'https://my-cover-url',
        display: { layout: 'one-item-medium' },
      },
    )
    expect(modules).toStrictEqual([offersWithCover])
  })

  it('should return a module for ExclusivityPane when an exclusivity module', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              alt: 'my alt text',
              image: {
                fields: {
                  file: {
                    url: '//my-image-url',
                  },
                },
              },
              offerId: 'AE',
              title: 'my title',
            },
            sys: {
              contentType: {
                sys: { id: CONTENT_TYPES.EXCLUSIVITY },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    const exclusivityPane = new ExclusivityPane({
        alt: 'my alt text',
        image: 'https://my-image-url',
        offerId: 'AE',
      },
    )
    expect(modules).toStrictEqual([exclusivityPane])
  })

  it('should fetch homepage preview when entry id is provided', async () => {
    // given
    const mockGetEntry = jest.fn().mockResolvedValue({
      fields: {
        modules: [{ fields: {} }],
      },
    })
    const mockGetEntries = jest.fn().mockResolvedValue({
      items: [module],
    })
    createClient.mockReturnValue({
      getEntry: mockGetEntry,
      getEntries: mockGetEntries,
    })
    const entryId = 'ABCDE'

    // when
    await fetchHomepage({ entryId: entryId })

    // then
    expect(createClient).toHaveBeenCalledWith({
      accessToken: CONTENTFUL_PREVIEW_TOKEN,
      environment: CONTENTFUL_ENVIRONMENT,
      host: "preview.contentful.com",
      space: CONTENTFUL_SPACE_ID,
    })
    expect(mockGetEntry).toHaveBeenCalledWith(entryId, { 'include': 2 })
    expect(mockGetEntries).not.toHaveBeenCalled()
  })

  it('should return modules when entry id is provided and returns data', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              image: {
                fields: {
                  file: {
                    url: '//my-image-url',
                  },
                },
              },
              title: 'my-title',
              url: 'my-url',
            },
            sys: {
              contentType: {
                sys: { id: 'not an algolia module' },
              },
            },
          },
        ],
      },
    }
    const mockGetEntry = jest.fn().mockResolvedValue(module)
    createClient.mockReturnValue({
      getEntry: mockGetEntry,
    })
    const entryId = 'ABCDE'

    // when
    const modules = await fetchHomepage({ entryId: entryId })

    // then
    expect(modules).toStrictEqual([
      new BusinessPane({
        "firstLine": null,
        "image": "https://my-image-url",
        "secondLine": null,
        "url": "my-url",
      }),
    ])
  })

  it('should fetch last homepage when entry id is not provided', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              image: {
                fields: {
                  file: {
                    url: '//my-image-url',
                  },
                },
              },
              title: 'my-title',
              url: 'my-url',
            },
            sys: {
              contentType: {
                sys: { id: 'not an algolia module' },
              },
            },
          },
        ],
      },
    }
    const mockGetEntry = jest.fn().mockResolvedValue({
      entry: {},
    })
    const mockGetEntries = jest.fn().mockResolvedValue({
      items: [module],
    })
    createClient.mockReturnValue({
      getEntries: mockGetEntries,
    })

    // when
    await fetchHomepage()

    // then
    expect(createClient).toHaveBeenCalledWith({
      accessToken: CONTENTFUL_ACCESS_TOKEN,
      environment: CONTENTFUL_ENVIRONMENT,
      space: CONTENTFUL_SPACE_ID,
    })
    expect(mockGetEntry).not.toHaveBeenCalled()
    expect(mockGetEntries).toHaveBeenCalledWith({ content_type: "homepage", "include": 2 })
  })

  it('should return an Offers module when "algoliaParameters" are provided but "displayParameters" are empty', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              algoliaParameters: {
                fields: {
                  isDuo: true,
                },
              },
              displayParameters: {
                fields: {},
              },
            },
            sys: {
              contentType: {
                sys: { id: CONTENT_TYPES.ALGOLIA },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    expect(modules).toStrictEqual([new Offers({
      algolia: { isDuo: true },
      display: {},
    })])
  })

  it('should return an empty array when fields of module "cover" are empty', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              algoliaParameters: {
                fields: {
                  isDuo: true,
                },
              },
              displayParameters: {
                fields: {
                  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
                },
              },
              cover: {},
            },
            sys: {
              contentType: {
                sys: { id: CONTENT_TYPES.ALGOLIA },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    expect(modules).toStrictEqual([])
  })

  it('should return an OffersWithCover when fields in "cover" are missing', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              algoliaParameters: {
                fields: {
                  isDuo: true,
                },
              },
              displayParameters: {
                fields: {
                  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
                },
              },
              cover: {
                fields: {},
              },
            },
            sys: {
              contentType: {
                sys: { id: CONTENT_TYPES.ALGOLIA },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    expect(modules).toStrictEqual([new OffersWithCover({
      algolia: {
        isDuo: true,
      },
      cover: null,
      display: {
        layout: 'one-item-medium',
      },
    })])
  })

  it('should return an OffersWithCover when file image of module "cover" is missing', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              algoliaParameters: {
                fields: {
                  isDuo: true,
                },
              },
              displayParameters: {
                fields: {
                  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
                },
              },
              cover: {
                fields: {
                  image: {
                    fields: {},
                  },
                },
              },
            },
            sys: {
              contentType: {
                sys: { id: CONTENT_TYPES.ALGOLIA },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    expect(modules).toStrictEqual([new OffersWithCover({
      algolia: {
        isDuo: true,
      },
      cover: null,
      display: {
        layout: "one-item-medium",
      },
    })])
  })

  it('should return an OffersWithCover when image url of module "cover" is missing', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              algoliaParameters: {
                fields: {
                  isDuo: true,
                },
              },
              displayParameters: {
                fields: {
                  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
                },
              },
              cover: {
                fields: {
                  image: {
                    fields: {
                      file: {},
                    },
                  },
                },
              },
            },
            sys: {
              contentType: {
                sys: { id: CONTENT_TYPES.ALGOLIA },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    expect(modules).toStrictEqual([new OffersWithCover({
      algolia: {
        isDuo: true,
      },
      cover: null,
      display: {
        layout: "one-item-medium",
      },
    })])
  })

  it('should return an empty array for BusinessPane when fields of image are missing', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              image: {
                fields: {
                  file: {},
                },
              },
            },
            sys: {
              contentType: {
                sys: { id: 'not an algolia module' },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    const business = new BusinessPane({
        firstLine: null,
        image: null,
        secondLine: null,
        url: null,
      },
    )
    expect(modules).toStrictEqual([business])
  })

  it('should return an empty array for ExclusivityPane when fields of image are missing', async () => {
    // given
    const module = {
      fields: {
        modules: [
          {
            fields: {
              alt: 'my alt text',
              image: {
                fields: {},
              },
              offerId: 'AE',
              title: 'my title',
            },
            sys: {
              contentType: {
                sys: { id: CONTENT_TYPES.EXCLUSIVITY },
              },
            },
          },
        ],
      },
    }
    createClient.mockReturnValue({
      getEntries: jest.fn().mockResolvedValue({
        items: [module],
      }),
    })

    // when
    const modules = await fetchHomepage()

    // then
    const exclusivityPane = new ExclusivityPane({
        alt: 'my alt text',
        image: null,
        offerId: 'AE',
      },
    )
    expect(modules).toStrictEqual([exclusivityPane])
  })
})
