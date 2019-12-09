import { Injectable, Injector } from '@angular/core';
import { HttpEvent, HttpInterceptor, HttpHandler, HttpRequest, HttpErrorResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { environment } from '../../../environments/environment';
import { UtilService } from '../services/util.service';
import { ApiRoutes } from '../constants/api-routes';

/**
 * Adds a default error handler to all requests.
 */
@Injectable()
export class ErrorHandlerInterceptor implements HttpInterceptor {

  constructor(private utilService: UtilService) { }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(catchError(error => this.errorHandler(error)));
  }

  // Customize the default error handler here if needed
  private errorHandler(response: HttpErrorResponse): Observable<HttpEvent<any>> {
    if (!environment.production) {
      // Do something with the error
    }
    if (!window.navigator.onLine) {
      // if there is no internet, throw a HttpErrorResponse error
      // since an error is thrown, the function will terminate here
      throw response;
    }
    if (response.error instanceof ErrorEvent) {
      console.error('Client Side Error => ', response.error.message);
    } else {
      console.error('Server Side Error => ', response);
      if (response.status === 504 || response.status === 0) {
        if(response.statusText.indexOf('Unknown')==0)
        {
          this.utilService.alert(`Redirecting to login page.`);
          this.goToUrl(ApiRoutes.loginRedirect);
        }
        else
          this.utilService.alert(`Unable to connect to server: ${response.statusText}`);
      } else if (response.status === 400) {
        this.utilService.alert(`Oops! Something went wrong and we could't process your request.`);
      }
    }
    if (response.error && response.error.message) {
      this.utilService.alert(response.error.message);
    }
    throw response;
  }
  private goToUrl(URL: any) {
    window.location.href = URL;
  }
}
