import { Injectable } from '@angular/core';
import { HttpEvent, HttpInterceptor, HttpHandler, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

/**
 * Prefixes all requests with `environment.serverUrl`.
 */
@Injectable()
export class ApiPrefixInterceptor implements HttpInterceptor {

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    let requestUrl = request.url;
    if (requestUrl.indexOf('http') === -1) {
      requestUrl = `${environment.serverUrl}${requestUrl}`;
    }
    request = request.clone({ url: requestUrl });
    console.log(request);
    return next.handle(request);
  }

}
