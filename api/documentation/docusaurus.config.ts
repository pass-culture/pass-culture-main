import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import type * as Redocusaurus from 'redocusaurus';

const env = process.env['ENV'];

const getOpenAPIJsonUrlFromEnv = (): string => {
  if (env === 'testing' || env === 'staging') {
    return `https://backend.${env}.passculture.team/openapi.json`;
  }
  if (env === 'production') {
    return 'https://backend.passculture.pro/openapi.json';
  }
  return 'http://localhost:5001/openapi.json';
}

const getDocumentationBaseUrlFromEnv = (): string => {
  if (env === 'testing' || env === 'staging') {
    return `https://developers.${env}.passculture.team`;
  }
  if (env === 'production') {
    return 'https://developers.passculture.pro';
  }
  return 'http://localhost:3000';
}


const config: Config = {
  title: 'Pass Culture documentation',
  tagline: '',
  favicon: 'img/favicon.ico',
  url: getDocumentationBaseUrlFromEnv(),
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  trailingSlash: false,
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
    // Redocusaurus config
    [
      'redocusaurus',
      {
        specs: [
          {
            spec: getOpenAPIJsonUrlFromEnv(),
            route: '/rest-api/',
          },
        ],
        theme: {
          primaryColor: '#6123df',
        },
      },
    ] satisfies Redocusaurus.PresetEntry,
  ],

  themeConfig: {
    image: 'img/pass-culture-social-card.jpg',
    colorMode: {
      disableSwitch: true,
    },
    navbar: {
      title: 'Pass Culture Developers',
      logo: {
        alt: 'Pass Culture Logo',
        src: 'img/passculture_logo.jpeg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'REST API',
          href: '/rest-api/',
        },
        {
          to: '/change-logs',
          label: 'Change logs',
          position: 'left',
        },
        {
          href: 'https://github.com/pass-culture/pass-culture-main',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Documentation',
              to: '/docs/category/mandatory-steps',
            },
            {
              label: 'REST API',
              to: '/rest-api',
            },
            {
              label: 'Change logs',
              to: '/change-logs',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'X',
              href: 'https://x.com/pass_Culture',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/pass-culture/pass-culture-main',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Pass Culture. Built with Docusaurus.`,
    },
    prism: {
      additionalLanguages: ['php', 'json', 'bash'],
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
