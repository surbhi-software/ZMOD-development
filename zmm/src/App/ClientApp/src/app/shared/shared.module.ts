import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { MaterialModule } from './material/material-module.module';
import { DropzoneModule } from 'ngx-dropzone-wrapper';

import { LoaderComponent } from './loader/loader.component';
import { AppDropzoneComponent } from './dropzone/dropzone.component';
import { SnackbarComponent } from './snackbar/snackbar.component';

import { ApiPrefixInterceptor } from './http/api-prefix.interceptor';
import { ErrorHandlerInterceptor } from './http/error-handler.interceptor';
import { CacheInterceptor } from './http/cache.interceptor';

import { HttpService } from './http/http.service';
import { HttpCacheService } from './http/http-cache.service';
import { UtilService } from './services/util.service';

import { FileSizePipe } from './pipes/file-size.pipe';
import { OrderByDatePipe } from '../shared/pipes/orderbydate.pipe';
import { HighlightPipe } from './pipes/highlight.pipe';
import { SearchFilterPipe } from './pipes/searchFilter.pipe';
import { SafePipe } from './pipes/safe.pipe';
import { ConfirmationbarComponent } from './confirmationbar/confirmationbar.component';
import { CronstruePipe } from './pipes/cronstrue.pipe';


@NgModule({
  imports: [
    CommonModule,
    HttpClientModule,
    MaterialModule,
    DropzoneModule
  ],
  declarations: [
    LoaderComponent,
    AppDropzoneComponent,
    FileSizePipe,
    SnackbarComponent,
    OrderByDatePipe,
    SearchFilterPipe,
    HighlightPipe,
    SafePipe,
    ConfirmationbarComponent,
    CronstruePipe
  ],
  exports: [
    MaterialModule,
    LoaderComponent,
    AppDropzoneComponent,
    FileSizePipe,
    SnackbarComponent,
    OrderByDatePipe,
    SearchFilterPipe,
    HighlightPipe,
    SafePipe,
    ConfirmationbarComponent,
    CronstruePipe
  ],
  providers: [
    UtilService,
    HttpService,
    HttpCacheService,
    ApiPrefixInterceptor,
    ErrorHandlerInterceptor,
    CacheInterceptor
  ],
  entryComponents: [
    SnackbarComponent
  ]
})
export class SharedModule { }
