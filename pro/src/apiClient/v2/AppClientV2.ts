/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';

import { ApiContremarqueService } from './services/ApiContremarqueService';
import { ApiOffresCollectivesBetaService } from './services/ApiOffresCollectivesBetaService';

type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;

export class AppClientV2 {

  public readonly apiContremarque: ApiContremarqueService;
  public readonly apiOffresCollectivesBeta: ApiOffresCollectivesBetaService;

  public readonly request: BaseHttpRequest;

  constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = FetchHttpRequest) {
    this.request = new HttpRequest({
      BASE: config?.BASE ?? 'http://localhost:5001',
      VERSION: config?.VERSION ?? '2',
      WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
      CREDENTIALS: config?.CREDENTIALS ?? 'include',
      TOKEN: config?.TOKEN,
      USERNAME: config?.USERNAME,
      PASSWORD: config?.PASSWORD,
      HEADERS: config?.HEADERS,
      ENCODE_PATH: config?.ENCODE_PATH,
    });

    this.apiContremarque = new ApiContremarqueService(this.request);
    this.apiOffresCollectivesBeta = new ApiOffresCollectivesBetaService(this.request);
  }
}

