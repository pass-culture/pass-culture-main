/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';

import { ApiContremarqueService } from './services/ApiContremarqueService';
import { ApiOffresCollectivesService } from './services/ApiOffresCollectivesService';

type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;

export class AppClientV2 {

  public readonly apiContremarque: ApiContremarqueService;
  public readonly apiOffresCollectives: ApiOffresCollectivesService;

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
    this.apiOffresCollectives = new ApiOffresCollectivesService(this.request);
  }
}

